# Antigravity スキル活用ガイド (`docs/skill_usage.md`)

本書では、AI コーディングアシスタント **Antigravity** が `plur` ライブラリの内部実装・API・自動化レシピを自律的に理解・活用するための **スキル（Skill）** の仕組み、配置場所、グローバル登録手順、および実際のプロンプトでの呼び出し方について解説します。

---

## 目次

1. [概要: Antigravity スキル (Skill) とは](#1-概要-antigravity-スキル-skill-とは)
2. [スキルのディレクトリ構成](#2-スキルのディレクトリ構成)
3. [配置場所の選択肢と探索メカニズム](#3-配置場所の選択肢と探索メカニズム)
4. [`~/.gemini/config/skills` へのリンク方法（推奨手順）](#4-geminiconfigskills-へのリンク方法推奨手順)
5. [Antigravity での使い方・プロンプト例](#5-antigravity-での使い方プロンプト例)
6. [スキルの更新とメンテナンス](#6-スキルの更新とメンテナンス)

---

## 1. 概要: Antigravity スキル (Skill) とは

Antigravity のスキルは、特定のリポジトリ、社内ツール、独自ライブラリの操作手順や API 仕様を AI アシスタントに「オンデマンドで注入」するための公式な知識拡張機能です。

### なぜルール (`GEMINI.md`) ではなくスキル (`SKILL.md`) なのか？
- **Progressive Disclosure (段階的開示)**:
  - ルールファイルは全ターン無条件にプロンプトへ注入され、トークンを常時消費してしまいます。
  - スキルは通常、`name` と `description` の数行のみが保持されます。「`plur` を使って CLI 自動化スクリプトを書いて」等の指示が出た際、AI が必要に応じて `SKILL.md` や詳細リファレンス（`references/`）、実装例（`examples/`）を動的に読み込みます。
- **体系化された設計**:
  - メイン指示書 (`SKILL.md`) に加えて、API 詳細や実行サンプルを階層構造で持てるため、AI が高精度なコードを生成できます。

---

## 2. スキルのディレクトリ構成

本リポジトリでは、以下の構成で `plur-automation` スキルを配置しています：

```text
plur/
├── .agents/
│   └── skills/
│       └── plur-automation/
│           ├── SKILL.md                 # Antigravity 向けメイン手順書 (Frontmatter付き)
│           ├── examples/                # 実動作するサンプルレシピ
│           │   ├── basic_bash.py        # ローカル bash 自動化例
│           │   ├── ssh_automation.py    # SSH リモート接続 & su 昇格例
│           │   └── hcm_integration.py  # Host Credential Manager 辞書との連携例
│           └── references/              # 詳細内部仕様・API カタログ
│               ├── architecture.md      # Session, Spawn, Node スタック, pty 構造
│               └── base_shell_api.md    # base_shell の主要関数一覧
└── docs/
    └── skill_usage.md                   # 本書
```

---

## 3. 配置場所の選択肢と探索メカニズム

Antigravity は以下の 2 つのスコープでスキルを自動検出します。

| スコープ | パス | 特徴 | 適した用途 |
| :--- | :--- | :--- | :--- |
| **ワークスペース** (プロジェクト単位) | `plur/.agents/skills/plur-automation/` | Git で管理され、チームや別環境と同期可能。<br/>Antigravity で `plur` リポジトリを開いているときに有効。 | `plur` 自体の開発・メンテナンス時 |
| **グローバル** (マシン全体) | `~/.gemini/config/skills/plur-automation/` | マシン内の**全プロジェクト**から常時参照可能。<br/>他アプリ（例: `host-credential-manager-go` など）の作業中でも即座に呼び出せる。 | `plur` を外部ツールとして利用する応用開発時 |

---

## 4. `~/.gemini/config/skills` へのリンク方法（推奨手順）

Git 管理（リポジトリ内資産）と、全プロジェクトからの横断利用を両立するため、**グローバル設定ディレクトリへのシンボリックリンク** を設定することを強く推奨します。

### 設定コマンド

ターミナルで以下のコマンドを実行します：

```bash
# 1. グローバルの skills ディレクトリを作成（初回のみ）
mkdir -p ~/.gemini/config/skills

# 2. plur リポジトリのスキルディレクトリへシンボリックリンクを作成 (絶対パスで指定)
ln -sfn /home/worker/Documents/antigravity/plur/.agents/skills/plur-automation ~/.gemini/config/skills/plur-automation

# 3. リンクが正常に作成されたか確認
ls -l ~/.gemini/config/skills/plur-automation
```

### 正常な出力例:
```text
lrwxrwxrwx 1 worker worker 70 Oct 29 16:54 /home/worker/.gemini/config/skills/plur-automation -> /home/worker/Documents/antigravity/plur/.agents/skills/plur-automation
```

これで、`host-credential-manager-go` や他のあらゆる作業ディレクトリを開いているときでも、Antigravity は `plur-automation` スキルを認識して自動活用できるようになります。

---

## 5. Antigravity での使い方・プロンプト例

スキルが配置（またはリンク）されている状態で、Antigravity に対して以下のように自然言語で指示を出すだけで、自動的に `plur-automation` スキルが起動されます。

### プロンプト例 1: ローカル自動化スクリプトの作成
> 「`plur` を使って、ローカルマシンのカーネルバージョンを取得し、`/tmp/audit.log` に結果を書き込むスクリプトを作って」

- **AI の挙動**:
  - `plur-automation` スキルを参照し、`@session_wrap.bash()` デコレータと `base_shell.run()`, `base_shell.here_doc()` を組み合わせた推奨コードを出力します。

### プロンプト例 2: リモートサーバーの監視・昇格操作
> 「`plur` を使って、リモート Linux サーバー（AlmaLinux 9）に SSH ログインし、`su` で root に切り替えて `systemctl status firewalld` を確認後、一般ユーザーに戻ってセッションを抜けるレシピを作って」

- **AI の挙動**:
  - `base_node.Linux` の定義、`@session_wrap.ssh()`、`session.su(user='root')`、`session.su_exit()` のライフサイクルに則ったコードを生成します。

### プロンプト例 3: Host Credential Manager (HCM) とのデータ連携
> 「Host Credential Manager のホスト辞書データ（`hostname`, `ip`, `username`, `password`, `platform`）を受け取って、`plur` で順次疎通確認とディスク使用率を取得するバッチスクリプトを書いて」

- **AI の挙動**:
  - `plur.session_wrap_by_node_dict` を活用した効率的な辞書連携レシピを即座に生成します。

---

## 6. スキルの更新とメンテナンス

`plur` に新しい関数やモジュールを追加した場合、以下のファイルを更新することで、Antigravity に常に最新の実装情報を認知させることができます：

1. **クイックリファレンスの更新**:
   [`SKILL.md`](file:///home/worker/Documents/antigravity/plur/.agents/skills/plur-automation/SKILL.md) のコードスニペットや一覧表を更新。
2. **詳細 API の更新**:
   [`references/base_shell_api.md`](file:///home/worker/Documents/antigravity/plur/.agents/skills/plur-automation/references/base_shell_api.md) に新規関数を追加。
3. **動作例の追加**:
   [`examples/`](file:///home/worker/Documents/antigravity/plur/.agents/skills/plur-automation/examples/) にユースケースに応じた実働 Python スクリプトを追加。

シンボリックリンクで接続されているため、`plur/.agents/skills/plur-automation/` 配下のファイルを Git 管理下で編集・コミットするだけで、グローバル側の Antigravity にも即座に最新情報が反映されます。
