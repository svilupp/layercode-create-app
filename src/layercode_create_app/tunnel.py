"""Cloudflare tunnel launcher utility."""

from __future__ import annotations

import asyncio
import contextlib
import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

from loguru import logger

TUNNEL_PATTERN = re.compile(r"https://[a-z0-9-]+\.trycloudflare\.com", re.IGNORECASE)


class CloudflareTunnelLauncher:
    """Launches a Cloudflare quick tunnel and surfaces the webhook URL."""

    def __init__(self, host: str, port: int, agent_route: str, binary: str = "cloudflared") -> None:
        self.host = host
        self.port = port
        self.agent_route = agent_route
        self.binary = binary
        self.process: asyncio.subprocess.Process | None = None
        self._stdout_task: asyncio.Task[None] | None = None
        self._stderr_task: asyncio.Task[None] | None = None
        self._tunnel_url: str | None = None
        self._log_file_handle: Any | None = None

        # Create log file for tunnel output
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file_path = Path(f"cloudflare_tunnel_{timestamp}.log")

    async def start(self, timeout_seconds: float = 30.0) -> str:
        """Start the tunnel and return the webhook URL."""

        if shutil.which(self.binary) is None:
            raise RuntimeError(
                "cloudflared binary not found. Install it from https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/"
            )

        # Open log file for writing (line-buffered for immediate output)
        self._log_file_handle = open(  # noqa: ASYNC230
            self.log_file_path, "w", encoding="utf-8", buffering=1
        )
        self._log_file_handle.write(
            f"=== Cloudflare Tunnel Log - {datetime.now().isoformat()} ===\n"
        )
        self._log_file_handle.write(f"Target: http://{self.host}:{self.port}\n")
        self._log_file_handle.write(f"Agent route: {self.agent_route}\n")
        self._log_file_handle.write("=" * 60 + "\n\n")
        self._log_file_handle.flush()

        target_host = "localhost" if self.host in {"0.0.0.0", ""} else self.host
        target = f"http://{target_host}:{self.port}"

        logger.info("Starting Cloudflare tunnel...")
        logger.info(f"Tunnel logs: {self.log_file_path.absolute()}")

        self.process = await asyncio.create_subprocess_exec(
            self.binary,
            "tunnel",
            "--url",
            target,
            "--loglevel",
            "debug",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        assert self.process.stdout is not None
        assert self.process.stderr is not None

        # Cloudflared outputs the URL to stderr, so we need to monitor both streams
        url_future: asyncio.Future[str] = asyncio.Future()

        # Store references for type checking
        stdout = self.process.stdout
        stderr = self.process.stderr

        async def monitor_streams() -> None:
            """Monitor both stdout and stderr for the tunnel URL."""
            stdout_task = asyncio.create_task(self._scan_for_url(stdout, "stdout", url_future))
            stderr_task = asyncio.create_task(self._scan_for_url(stderr, "stderr", url_future))

            # Wait for either task to find the URL
            done, pending = await asyncio.wait(
                {stdout_task, stderr_task}, return_when=asyncio.FIRST_COMPLETED
            )

            # Cancel the other task
            for task in pending:
                task.cancel()
                with contextlib.suppress(asyncio.CancelledError):
                    await task

        try:
            # Start monitoring both streams
            monitor_task = asyncio.create_task(monitor_streams())
            tunnel_url = await asyncio.wait_for(url_future, timeout=timeout_seconds)
            await monitor_task
        except TimeoutError as exc:
            await self.stop()
            raise RuntimeError("Timed out waiting for Cloudflare tunnel URL") from exc

        self._stdout_task = asyncio.create_task(self._drain_stream(self.process.stdout, "stdout"))
        self._stderr_task = asyncio.create_task(self._drain_stream(self.process.stderr, "stderr"))

        self._tunnel_url = tunnel_url
        webhook_path = self.agent_route.lstrip("/")
        webhook_url = f"{tunnel_url}/{webhook_path}" if webhook_path else tunnel_url

        logger.info("Tunnel established successfully")
        logger.info(f"Webhook URL: {webhook_url}")
        _print_banner(tunnel_url, webhook_url)
        return webhook_url

    async def _scan_for_url(
        self, stream: asyncio.StreamReader, stream_name: str, url_future: asyncio.Future[str]
    ) -> None:
        """Scan a stream for the tunnel URL and log all output to file only."""
        try:
            while True:
                line = await stream.readline()
                if not line:
                    break
                decoded = line.decode("utf-8", errors="ignore")

                # Write to log file only (not to console)
                if self._log_file_handle:
                    self._log_file_handle.write(f"[{stream_name}] {decoded}")
                    self._log_file_handle.flush()

                # Check if this line contains the tunnel URL
                match = TUNNEL_PATTERN.search(decoded)
                if match and not url_future.done():
                    url = match.group(0)
                    url_future.set_result(url)
                    return
        except asyncio.CancelledError:
            # This is expected when the URL is found in the other stream
            pass

    async def _drain_stream(self, stream: asyncio.StreamReader, stream_name: str) -> None:
        """Drain output from tunnel process and write to log file only."""
        while True:
            line = await stream.readline()
            if not line:
                break
            decoded = line.decode("utf-8", errors="ignore")

            # Write to log file only (not to console)
            if self._log_file_handle:
                self._log_file_handle.write(f"[{stream_name}] {decoded}")
                self._log_file_handle.flush()

    async def stop(self) -> None:
        """Stop the tunnel process and clean up resources."""
        if self.process and self.process.returncode is None:
            self.process.terminate()
            try:
                await asyncio.wait_for(self.process.wait(), timeout=5)
            except TimeoutError:
                self.process.kill()
                await self.process.wait()

        for task in (self._stdout_task, self._stderr_task):
            if task:
                task.cancel()
                with contextlib.suppress(asyncio.CancelledError):
                    await task

        # Close log file
        if self._log_file_handle:
            self._log_file_handle.write(
                f"\n=== Tunnel stopped at {datetime.now().isoformat()} ===\n"
            )
            self._log_file_handle.close()
            self._log_file_handle = None
            logger.info(f"Tunnel logs saved to: {self.log_file_path.absolute()}")


def _print_banner(tunnel_url: str, webhook_url: str) -> None:
    """Print a prominent banner with tunnel URLs."""
    border = "=" * 70
    message = (
        f"\n\n{border}\n"
        f"{border}\n"
        "  ✓ CLOUDFLARE TUNNEL ESTABLISHED\n"
        f"{border}\n\n"
        f"  Webhook URL: {webhook_url}\n\n"
        f"{border}\n"
        "  IMPORTANT: Add this webhook URL to your LayerCode agent:\n"
        "  https://dash.layercode.com/\n"
        f"{border}\n"
        f"{border}\n\n"
    )
    print(message, flush=True)
