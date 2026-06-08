# D-
COMMANDER_VAULT
FileSentinel/
│
├── sentinel.py          # 主程式
├── snapshot.json       # 快照資料
├── diff_report.json    # 差異報告
└── restore_index.json  # 還原索引

[Watcher Engine]
               ↓
        [Event Logger]
               ↓
        [Snapshot DB]
               ↓
        [Diff Analyzer]
               ↓
        [Restore Index]
               ↓
        [Report System]
        FileSentinelEnterprise/
│
├── watcher.py          # 即時監控核心
├── snapshot.py         # 快照系統
├── analyzer.py         # 差異分析
├── restore.py          # 還原索引
├── logs/
│    └── events.json
├── snapshots/
│    └── latest.json
└── reports/
     └── diff.json
     
