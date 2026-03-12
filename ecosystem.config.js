module.exports = {
  apps: [
    {
      name: 'gmail-watcher',
      script: './watchers/gmail_watcher.py',
      interpreter: 'python3',
      args: '--vault ./vault',
      cwd: '/home/muhammad_tayyab/hackathon/Personal_AI_Employee',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '500M',
      env: {
        VAULT_PATH: './vault',
        GMAIL_TOKEN_PATH: './vault/secrets/gmail_token.json',
        GMAIL_CREDENTIALS_PATH: './vault/secrets/gmail_credentials.json'
      },
      error_file: './vault/Logs/pm2-gmail-watcher-error.log',
      out_file: './vault/Logs/pm2-gmail-watcher-out.log',
      log_file: './vault/Logs/pm2-gmail-watcher-combined.log',
      time: true
    },
    {
      name: 'orchestrator',
      script: './orchestrator.py',
      interpreter: 'python3',
      args: '--vault ./vault --live',
      cwd: '/home/muhammad_tayyab/hackathon/Personal_AI_Employee',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '500M',
      env: {
        VAULT_PATH: './vault',
        DRY_RUN: 'false'
      },
      error_file: './vault/Logs/pm2-orchestrator-error.log',
      out_file: './vault/Logs/pm2-orchestrator-out.log',
      log_file: './vault/Logs/pm2-orchestrator-combined.log',
      time: true
    }
  ]
};
