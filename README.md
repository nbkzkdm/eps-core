# eps-core

EPS (Entry Point System)

シェルコマンドを登録・再利用・実行するためのCLIツールです。  
`$1`, `$2` などのプレースホルダーを使って、実行時に値を差し込めます。

---

## Install

```bash
pip install -e .
```

---

## 基本コンセプト

- コマンドを登録して再利用する
- `$1`, `$2` で引数を後から入力可能
- CLIから直接実行・確認・編集できる

---

## コマンド一覧

| コマンド | 内容 |
|----------|------|
| entry   | コマンド登録 |
| exe     | 実行 |
| view    | 表示 |
| modify  | 編集 |
| delete  | 削除 |
| save    | ファイル保存 |
| load    | ファイル読み込み |
| settings| 設定管理 |

---

## entry（登録）

```bash
eps entry echo '$1' --name sample01
```

- `--name` 未指定の場合は自動生成
- 自動生成ルール：スペース → ハイフン

```bash
eps entry echo hello
# → name: echo-hello
```

### 重複時

```
[ERROR] Entry 'xxx' already exists.
Use --force to overwrite.
```

```bash
eps entry echo hello --name sample01 --force
```

---

## exe（実行）

### 直接引数指定

```bash
eps exe sample01 goodmorning
```

```
[COMMAND] echo goodmorning
[RESULT]
goodmorning
```

### 入力待ち

```bash
eps exe sample01
```

```
args1: goodmorning
```

---

## view（表示）

```bash
eps view sample01
```

```bash
eps view --all
```

---

## modify（編集）

```bash
eps modify sample01
```

```
[CURRENT] echo $1
[NEW COMMAND] echo hello
```

---

## delete（削除）

```bash
eps delete sample01
```

```
Delete this entry? [y/N]:
```

---

## save（ファイル保存）

```bash
eps save
```

保存先：

```
~/eps-settings.json
```

上書き時：

```
Overwrite this file? [y/N]:
```

### フォーマット

```json
{
  "entries": [
    {"name": "sample01", "command": "echo $1"}
  ]
}
```

---

## load（読み込み）

```bash
eps load file.json
```

### 動作

- entries をマージ
- name重複時は自動リネーム

```
sample01 → sample012
```

---

### オプション

重複時の処理オプション

#### スキップ

```bash
eps load file.json --skip
```

```
[SKIP] sample01
```

#### 上書き

```bash
eps load file.json --force
```

```
[OVERWRITE] sample01
```

---

## settings（設定）

### 表示

```bash
eps settings view
```

```
save.file.path: ~
save.file.name: eps-settings.json
```

---

### 変更

```bash
eps settings modify save.file.path
```

```
[CURRENT] save.file.path: ~
[NEW VALUE] /home/user
```

---

## プレースホルダー仕様

使用可能：

```
$1, $2, $3 ...
```

例：

```bash
eps entry echo '$1 $2' --name sample02
eps exe sample02 hello world
```

---

## データ保存

内部ストア：

```
~/.eps/store.json
```

- 毎回ロード / 保存（常駐しない）
- CLI終了後もデータ保持

