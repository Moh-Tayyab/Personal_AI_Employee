/**
 * PM2 Ecosystem Configuration for Personal AI Employee
 *
 * Manages the orchestrator and all watchers as persistent services
 * with automatic restart on failure, log rotation, and graceful shutdown.
 *
 * Usage:
 *   pm2 start ecosystem.config.js
 *   pm2 stop ecosystem.config.js
 *   pm2 restart ecosystem.config.js
 *   pm2 delete ecosystem.config.js
 *   pm2 monit
 */

// Resolve absolute paths from project root
const path = require('path');
const projectRoot = __dirname;
const vaultPath = path.join(projectRoot, 'vault');
const venvPython = path.join(projectRoot, '.venv', 'bin', 'python');

module.exports = {
  apps: [
    // ============================================================
    // Orchestrator — Central coordinator (always running)
    // ============================================================
    {
      name: 'ai-orchestrator',
      script: venvPython,
      args: 'orchestrator.py --vault ./vault',
      cwd: projectRoot,
      env_file: '.env',
      env: {
        VAULT_PATH: vaultPath,
        DRY_RUN: 'true',        // Set to 'false' for production
        HEALTH_PORT: '8080',
      },
      instances: 1,
      exec_mode: 'fork',
      max_memory_restart: '500M',
      restart_delay: 5000,      // 5s delay before auto-restart
      max_restarts: 10,         // Give up after 10 crashes
      min_uptime: '60s',        // Consider crash if dies within 60s
      kill_timeout: 10000,      // 10s grace period for graceful shutdown
      wait_ready: true,
      listen_timeout: 15000,
      error_file: './logs/pm2/orchestrator-error.log',
      out_file: './logs/pm2/orchestrator-out.log',
      merge_logs: true,
      autorestart: true,
    },

    // ============================================================
    // Gmail Watcher — Monitors Gmail for important emails
    // ============================================================
    {
      name: 'gmail-watcher',
      script: venvPython,
      args: 'watchers/gmail_watcher.py --vault ./vault',
      cwd: projectRoot,
      env_file: '.env',
      env: {
        VAULT_PATH: vaultPath,
      },
      instances: 1,
      exec_mode: 'fork',
      max_memory_restart: '300M',
      restart_delay: 5000,
      max_restarts: 10,
      min_uptime: '30s',
      kill_timeout: 5000,
      error_file: './logs/pm2/gmail-watcher-error.log',
      out_file: './logs/pm2/gmail-watcher-out.log',
      merge_logs: true,
      autorestart: true,
    },

    // ============================================================
    // Filesystem Watcher — Monitors drop folder for new files
    // ============================================================
    {
      name: 'filesystem-watcher',
      script: venvPython,
      args: 'watchers/filesystem_watcher.py --vault ./vault --drop-dir ./drop',
      cwd: projectRoot,
      env_file: '.env',
      env: {
        VAULT_PATH: vaultPath,
      },
      instances: 1,
      exec_mode: 'fork',
      max_memory_restart: '300M',
      restart_delay: 5000,
      max_restarts: 10,
      min_uptime: '30s',
      kill_timeout: 5000,
      error_file: './logs/pm2/filesystem-watcher-error.log',
      out_file: './logs/pm2/filesystem-watcher-out.log',
      merge_logs: true,
      autorestart: true,
    },

    // ============================================================
    // WhatsApp Watcher — Monitors WhatsApp Web (optional)
    // DISABLED by default — enable when WhatsApp credentials are set
    // ============================================================
    // {
    //   name: 'whatsapp-watcher',
    //   script: venvPython,
    //   args: 'watchers/whatsapp_watcher.py --vault ./vault --headless',
    //   cwd: projectRoot,
    //   env_file: '.env',
    //   env: {
    //     VAULT_PATH: vaultPath,
    //   },
    //   instances: 1,
    //   exec_mode: 'fork',
    //   max_memory_restart: '500M',
    //   restart_delay: 10000,
    //   max_restarts: 5,
    //   min_uptime: '60s',
    //   kill_timeout: 10000,
    //   error_file: './logs/pm2/whatsapp-watcher-error.log',
    //   out_file: './logs/pm2/whatsapp-watcher-out.log',
    //   merge_logs: true,
    //   autorestart: true,
    // },
  ],
};
