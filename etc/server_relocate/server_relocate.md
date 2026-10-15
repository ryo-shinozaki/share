# ntserv_eng引っ越し

## 日程

- 2026年9月7-18日 帯域を絞り込んだファイルのコピー
- 2026年9月18日(金)16時45分 現行サーバーのパーミッション取得開始（この時刻以降新しいファイル及びディレクトリを配置しないでください）
- 2026年9月19日(土)8時 ファイルのコピー(更新分)（この時刻以降、ファイル及びディレクトリを更新しないでください)
- 2026年9月20日(日)8時 新サーバでパーミッション設定
- 2026年9月23日(水)8時 現行サーバーのシャットダウン()、新サーバーのIPアドレス、ホスト名を現行サーバーと一致させ再起動、種々テスト
- 2026年9月24日(木)8時 新サーバー運用開始（ファイル及びディレクトリの新規配置、更新ができます）


## サーバー名、およびアドレス

### 現ntserv_eng

- ホスト名: NTSRV-ENG
- プライマリ DNS サフィックス: nf.uniontool.co.jp
- ノード タイプ: ハイブリッド
- IP ルーティング有効: いいえ
- WINS プロキシ有効 : いいえ
- DNS サフィックス検索一覧: nf.uniontool.co.jp, uniontool.co.jp
- IPv4 アドレス : 192.168.2.210
- サブネット マスク : 255.255.255.0
- デフォルト ゲートウェイ : 192.168.2.1
- DNS サーバー: 192.168.2.79, 192.168.2.206
 
#### 共有ディレクトリ

| Name | ScopeName | Path | 共有先からどう見えるか |
| --- | --- | --- | --- |
| ace | * | `D:\ENG\ace` | `\\192.168.2.210\ace` |
| cad | * | `D:\ENG\cad` | `\\192.168.2.210\cad` |
| dio | * | `D:\ENG\dio` | `\\192.168.2.210\dio` |
| users | * | `D:\ENG\users` | `\\192.168.2.210\users` |
| users1 | * | `D:\ENG\users1` | `\\192.168.2.210\users1` |
| 取扱説明書 | * | `D:\ENG\取扱説明書` | `\\192.168.2.210\取扱説明書` |
| 機械機器見積 | * | `D:\ENG\機械機器見積` | `\\192.168.2.210\機械機器見積` |
| 製造番号管理 | * | `D:\ENG\製造番号管理` | `\\192.168.2.210\製造番号管理` |

#### ローカルユーザー

| Name | Enabled | Description | 備考
| --- | --- | --- | --- |
| shinbot | True | 新保貴也(gitlab) | PW:XXX
| shinozakir | True | 篠崎亮(gitlab) | 移転先では不要

### 移転先 ntserv_eng

- ホスト名:NTSRV-ENGN
- IPアドレス:192.168.2.152

ただし、ファイルのコピー、設定完了後、旧サーバーの設定と一致させる。

## 手順

### ローカルユーザーの追加

8月25日に完了

| Name | Enabled | Description | 備考
| --- | --- | --- | --- |
| shinbot | True | 新保貴也(gitlab) | PW:Union2620

### ファイルのコピー

旧サーバーの移行対象は、2026年8月26日時点で10,217,225ファイル、総容量11.8 TBである。新サーバー `NTSRV-ENGN` に、旧サーバーと新サーバーの両方でAdministrator権限を持つActive Directoryユーザーでログオンし、管理者として起動したPowerShellから実行する。

コピー元は旧サーバー（`192.168.2.210`）、コピー先は新サーバーの `D:\ENG` とする。RobocopyではNTFSアクセス許可、所有者および監査情報を含めてコピーする。共有名と共有アクセス許可はRobocopyでは移行されないため、別途設定する。

#### 事前確認

1. 新サーバーのコピー先ドライブに11.8 TB以上の空き容量があることを確認する。
1. 新サーバーから `\\192.168.2.210\製造番号管理` を参照できることを確認する。
1. PowerShellが管理者として起動されていることを確認する。
1. ログ保存先を作成する。

   ```powershell
   New-Item -ItemType Directory -Path D:\ENG\RobocopyLogs -Force
   ```

#### 小テスト（ace）

最初に、`D:\ENG\ace` を対象に、ファイルのコピーからSIDの置換までをテストする。

旧サーバーで管理者としてPowerShellを起動し、`D:\ENG\ace` のACLを保存する。`icacls /save` は既存の保存先ファイルを上書きしないため、同名ファイルが存在する場合は、内容が不要であることを確認して削除するか別名を使用する。処理件数を確認できるよう、保存時は `/Q` を付けない。

```powershell
$aclFile = "D:\ENG\acl-ace-test.txt"
if (Test-Path -LiteralPath $aclFile) {
    throw "ACL保存先が既に存在します。削除するか別名を指定してください: $aclFile"
}
icacls.exe "D:\ENG\ace" /save $aclFile /T /C
if ($LASTEXITCODE -ne 0 -or (Get-Item -LiteralPath $aclFile).Length -eq 0) {
    throw "ACLの保存に失敗したか、ACLファイルが空です。"
}
```

正常に処理されたファイル数が1件以上、処理できなかったファイル数が0件であることを確認する。

新サーバーで、ACLファイルを取得してから `D:\ENG\ace` へコピーする。

```powershell
Copy-Item "\\192.168.2.210\D$\ENG\acl-ace-test.txt" "D:\ENG\acl-ace-test.txt"
```

```powershell
robocopy "\\192.168.2.210\ace" "D:\ENG\ace" /E /COPYALL /DCOPY:DAT /ZB /R:2 /W:5 /XJ /TEE /LOG+:"D:\ENG\RobocopyLogs\ace-test.log"
```

Robocopyが完了したら、新サーバーでACL保存ファイルのコピーを作り、そのコピー内の旧SIDを新SIDへ置換する。`icacls /substitute` は、旧サーバーのローカルSIDを解決できずエラー1332（「アカウント名とセキュリティ ID の間のマッピングは実行されませんでした」）になるため使用しない。元のACL保存ファイルはロールバック用として変更せずに保持する。

```powershell
$source = "D:\ENG\acl-ace-test.txt"
$output = "D:\ENG\acl-ace-converted.txt"

if (Test-Path -LiteralPath $output) {
    throw "変換後ACLファイルが既に存在します: $output"
}

$sidMap = [ordered]@{
    "S-1-5-21-2751499492-1868010712-940411855-500"  = "S-1-5-21-1010608215-2051037059-1241265453-500"
    "S-1-5-21-2751499492-1868010712-940411855-503"  = "S-1-5-21-1010608215-2051037059-1241265453-503"
    "S-1-5-21-2751499492-1868010712-940411855-501"  = "S-1-5-21-1010608215-2051037059-1241265453-501"
    "S-1-5-21-2751499492-1868010712-940411855-1003" = "S-1-5-21-1010608215-2051037059-1241265453-1002"
    "S-1-5-21-2751499492-1868010712-940411855-504"  = "S-1-5-21-1010608215-2051037059-1241265453-504"
    "S-1-5-21-2751499492-1868010712-940411855-1000" = "S-1-5-21-1010608215-2051037059-1241265453-1003"
    "S-1-5-21-2751499492-1868010712-940411855-1002" = "S-1-5-21-1010608215-2051037059-1241265453-1001"
    "S-1-5-21-2751499492-1868010712-940411855-1001" = "S-1-5-21-1010608215-2051037059-1241265453-1000"
}

# icacls /save の出力はUTF-16LEとして明示的に読み込む。
# 文字コードを自動判定させると、各文字間にNUL文字が入った壊れたACLファイルになる場合がある。
$content = Get-Content -LiteralPath $source -Raw -Encoding Unicode
foreach ($oldSid in $sidMap.Keys) {
    $count = ([regex]::Matches($content, [regex]::Escape($oldSid))).Count
    Write-Host "$oldSid : $count 件"
    $content = $content.Replace($oldSid, $sidMap[$oldSid])
}
Set-Content -LiteralPath $output -Value $content -Encoding Unicode

if (Select-String -LiteralPath $output -Pattern ([char]0) -SimpleMatch -Quiet -Encoding Unicode) {
    throw "変換後ACLファイルにNUL文字が含まれています。復元しないでください。"
}
if (Select-String -LiteralPath $output -Pattern @($sidMap.Keys) -SimpleMatch -Quiet -Encoding Unicode) {
    throw "変換後ACLファイルに置換対象の旧SIDが残っています。復元しないでください。"
}
```

表示された置換件数を確認する。また、次のコマンドでファイル名とSDDLが文字間の空白なしで表示されることを確認してから、変換後のACLファイルを復元する。

```powershell
Get-Content -LiteralPath $output -Encoding Unicode -TotalCount 4
```

```powershell
icacls.exe "D:\ENG" /restore "D:\ENG\acl-ace-converted.txt" /C
```

保存対象を `D:\ENG\ace\*` にすると、継承元である `ace` フォルダー自身のACLが保存されない。そのため末尾の `\*` は付けない。この場合、ACLファイル内のパスは `ace` から始まるため、復元先にはその親ディレクトリである `D:\ENG` を指定する。

実行後、次を確認する。

1. Robocopyの終了コードが0から7であることを確認する。8以上の場合はエラーを解消して再実行する。
1. コピー元とコピー先のファイル数、フォルダー数および容量をRobocopyログで比較する。
1. コピー先のファイルを開けることを確認する。
1. ACL復元コマンドの処理失敗が0件であることを確認する。
1. ファイルとフォルダーの「セキュリティ」タブ、または `icacls` でNTFSアクセス許可が維持され、旧サーバーのSIDが「不明なアカウント」として残っていないことを確認する。

##### 所要時間の調査

全体のACL保存、SID置換およびACL復元に必要な時間を見積もるため、小テストの各処理時間を記録する。ファイル数だけでなくフォルダー数もACL処理の対象になるため、両方を含む項目数を使用する。

旧サーバーで、ACL保存前に次を実行する。項目数の走査自体にも時間がかかるため、その時間はACL保存時間と分けて記録する。

```powershell
$testPath = "D:\ENG\ace"
$resultFile = "D:\ENG\acl-ace-timing.json"

$countWatch = [System.Diagnostics.Stopwatch]::StartNew()
$itemCount = 1 + @(
    Get-ChildItem -LiteralPath $testPath -Force -Recurse -ErrorAction Stop
).Count
$countWatch.Stop()

$aclFile = "D:\ENG\acl-ace-timing.txt"
if (Test-Path -LiteralPath $aclFile) {
    throw "ACL保存先が既に存在します: $aclFile"
}

$saveWatch = [System.Diagnostics.Stopwatch]::StartNew()
icacls.exe $testPath /save $aclFile /T /C
$saveExitCode = $LASTEXITCODE
$saveWatch.Stop()
if ($saveExitCode -ne 0 -or (Get-Item -LiteralPath $aclFile).Length -eq 0) {
    throw "ACLの保存に失敗したか、ACLファイルが空です。終了コード: $saveExitCode"
}

[ordered]@{
    TestPath           = $testPath
    ItemCount          = $itemCount
    CountSeconds       = $countWatch.Elapsed.TotalSeconds
    AclSaveSeconds     = $saveWatch.Elapsed.TotalSeconds
    AclFileBytes       = (Get-Item -LiteralPath $aclFile).Length
    SidReplaceSeconds  = $null
    AclRestoreSeconds  = $null
} | ConvertTo-Json | Set-Content -LiteralPath $resultFile -Encoding UTF8

Get-Content -LiteralPath $resultFile
```

作成された `acl-ace-timing.txt` と `acl-ace-timing.json` を新サーバーの `D:\ENG` へコピーする。新サーバーでは、次のスクリプトでSID置換とACL復元の時間を測定し、全体に対する推定時間を表示する。SIDの対応は小テストで使用した `$sidMap` と同じである。`$totalItemCount` には、Robocopyログなどで確認した全体のファイル数とフォルダー数の合計を設定する。フォルダー数がまだ不明な場合、初期値の10,217,225件はファイル数だけなので、表示結果は下限の目安となる。

```powershell
Copy-Item "\\192.168.2.210\D$\ENG\acl-ace-timing.txt" "D:\ENG\acl-ace-timing.txt"
Copy-Item "\\192.168.2.210\D$\ENG\acl-ace-timing.json" "D:\ENG\acl-ace-timing.json"
```

```powershell
$source = "D:\ENG\acl-ace-timing.txt"
$output = "D:\ENG\acl-ace-timing-converted.txt"
$resultFile = "D:\ENG\acl-ace-timing.json"
$totalItemCount = 10217225 # ファイル数とフォルダー数の合計が判明したら置き換える

if (Test-Path -LiteralPath $output) {
    throw "変換後ACLファイルが既に存在します: $output"
}

$sidMap = [ordered]@{
    "S-1-5-21-2751499492-1868010712-940411855-500"  = "S-1-5-21-1010608215-2051037059-1241265453-500"
    "S-1-5-21-2751499492-1868010712-940411855-503"  = "S-1-5-21-1010608215-2051037059-1241265453-503"
    "S-1-5-21-2751499492-1868010712-940411855-501"  = "S-1-5-21-1010608215-2051037059-1241265453-501"
    "S-1-5-21-2751499492-1868010712-940411855-1003" = "S-1-5-21-1010608215-2051037059-1241265453-1002"
    "S-1-5-21-2751499492-1868010712-940411855-504"  = "S-1-5-21-1010608215-2051037059-1241265453-504"
    "S-1-5-21-2751499492-1868010712-940411855-1000" = "S-1-5-21-1010608215-2051037059-1241265453-1003"
    "S-1-5-21-2751499492-1868010712-940411855-1002" = "S-1-5-21-1010608215-2051037059-1241265453-1001"
    "S-1-5-21-2751499492-1868010712-940411855-1001" = "S-1-5-21-1010608215-2051037059-1241265453-1000"
}

$result = Get-Content -LiteralPath $resultFile -Raw -Encoding UTF8 | ConvertFrom-Json
$replaceWatch = [System.Diagnostics.Stopwatch]::StartNew()
$content = Get-Content -LiteralPath $source -Raw -Encoding Unicode
foreach ($oldSid in $sidMap.Keys) {
    $content = $content.Replace($oldSid, $sidMap[$oldSid])
}
Set-Content -LiteralPath $output -Value $content -Encoding Unicode

if (Select-String -LiteralPath $output -Pattern @($sidMap.Keys) -SimpleMatch -Quiet -Encoding Unicode) {
    throw "変換後ACLファイルに置換対象の旧SIDが残っています。"
}
$replaceWatch.Stop()

$restoreWatch = [System.Diagnostics.Stopwatch]::StartNew()
icacls.exe "D:\ENG" /restore $output /C
$restoreExitCode = $LASTEXITCODE
$restoreWatch.Stop()
if ($restoreExitCode -ne 0) {
    throw "ACLの復元でエラーが発生しました。終了コード: $restoreExitCode"
}

$result.SidReplaceSeconds = $replaceWatch.Elapsed.TotalSeconds
$result.AclRestoreSeconds = $restoreWatch.Elapsed.TotalSeconds
$result | ConvertTo-Json | Set-Content -LiteralPath $resultFile -Encoding UTF8

$scale = $totalItemCount / [double]$result.ItemCount
[pscustomobject]@{
    TestItemCount          = $result.ItemCount
    Scale                  = [math]::Round($scale, 2)
    EstimatedSaveHours     = [math]::Round($result.AclSaveSeconds * $scale / 3600, 2)
    EstimatedReplaceHours  = [math]::Round($result.SidReplaceSeconds * $scale / 3600, 2)
    EstimatedRestoreHours  = [math]::Round($result.AclRestoreSeconds * $scale / 3600, 2)
    EstimatedTotalHours    = [math]::Round(
        ($result.AclSaveSeconds + $result.SidReplaceSeconds + $result.AclRestoreSeconds) * $scale / 3600,
        2
    )
} | Format-List
```

この推定は項目数に比例すると仮定した概算である。共有ごとのファイルサイズ、ディレクトリ構成、ACLの複雑さ、ストレージ性能およびウイルス対策ソフトの影響を受けるため、表示結果に1.5倍から2倍程度の余裕を持たせる。

#### 初回コピー（2026年9月7日～18日）

小テストに問題がなければ、全共有ディレクトリをコピーする。業務時間中のネットワーク負荷を抑えるため、`/IPG:5` から開始する。`/IPG` はパケット送信間隔をミリ秒単位で空ける方式であり、正確な帯域値を指定するものではない。実際のネットワーク負荷と進捗を確認し、値を大きくすると低速、小さくすると高速になるよう調整する。

```powershell
$shares = @('ace', 'cad', 'dio', 'users', 'users1', '取扱説明書', '機械機器見積', '製造番号管理')
foreach ($share in $shares) {
    robocopy "\\192.168.2.210\$share" "D:\ENG\$share" /MIR /E /COPYALL /DCOPY:DAT /ZB /R:2 /W:5 /XJ /TEE /MT:24 /LOG+:"D:\ENG\RobocopyLogs\$share-initial.log"
    if ($LASTEXITCODE -ge 8) {
        Write-Warning "$share のコピーでエラーが発生しました。終了コード: $LASTEXITCODE"
    }
}
```

コピーは中断後に同じコマンドを再実行できる。既にコピー済みで変更のないファイルはスキップされる。

##### 初回コピー履歴

- 2026年9月7日7時54分開始  
- 低速だったため、9月7日8時10分に、帯域制限を解除し、コピーを再開
- 低速だったため、9月7日10時に、/MT:16オプション追加

#### 最終差分コピー（2026年9月19日）

初回コピー開始後に更新されたファイルと、新規に作成されたファイルをコピーする。ファイルの整合性を保つため、実行前に利用者へ作業開始を通知し、旧サーバーの共有ディレクトリへの書き込みを停止する。

最終差分コピーでは短時間での完了を優先し、帯域制限を外して次のコマンドを実行する。Robocopyはコピー元とコピー先を比較し、初回コピー後に更新または新規作成されたファイルをコピーする。

```powershell
$shares = @('ace', 'cad', 'dio', 'users', 'users1', '取扱説明書', '機械機器見積', '製造番号管理')
foreach ($share in $shares) {
    robocopy "\\192.168.2.210\$share" "D:\ENG\$share" /MIR /E /COPYALL /DCOPY:DAT /ZB /R:2 /W:5 /XJ /TEE /MT:24 /LOG+:"D:\ENG\RobocopyLogs\$share-final.log"
    if ($LASTEXITCODE -ge 8) {
        Write-Warning "$share の差分コピーでエラーが発生しました。終了コード: $LASTEXITCODE"
    }
}
```

完了後、各ログについて終了コードが0から7であること、失敗（`FAILED`）が0件であることを確認する。確認が完了するまで旧サーバーへの書き込みを再開しない。

#### ローカルユーザーおよびローカルグループのアクセス許可移行

旧サーバーと新サーバーに同名のローカルユーザーまたはローカルグループが存在しても、それぞれのSIDは異なる。Robocopyの `/COPYALL` はアクセス許可に記録された旧サーバーのSIDをそのままコピーするため、新サーバーの同名アカウントには自動的に対応付けられない。

可能なものは、移行前にNTFSアクセス許可をActive Directoryのユーザーまたはグループへ変更する。Active Directoryアカウントを使用できず、新サーバーのローカルアカウントを引き続き使用する場合は、以下の手順で旧SIDを新SIDへ置換する。

##### 1. SIDの確認

旧サーバーと新サーバーのそれぞれで、管理者として起動したPowerShellから次を実行する。

```powershell
Get-LocalUser | Select-Object Name, SID
Get-LocalGroup | Select-Object Name, SID
```

同名アカウントを取り違えないよう、置換対象を次の表に記録する。

| 種別 | 名前 | 旧サーバーのSID | 新サーバーのSID |
| --- | --- | --- | --- |
| ローカルユーザー | Administrator | S-1-5-21-2751499492-1868010712-940411855-500 | S-1-5-21-1010608215-2051037059-1241265453-500 |
| ローカルユーザー | DefaultAccount | S-1-5-21-2751499492-1868010712-940411855-503 | S-1-5-21-1010608215-2051037059-1241265453-503 |
| ローカルユーザー | Guest | S-1-5-21-2751499492-1868010712-940411855-501 | S-1-5-21-1010608215-2051037059-1241265453-501 |
| ローカルユーザー | shinbot | S-1-5-21-2751499492-1868010712-940411855-1003 | S-1-5-21-1010608215-2051037059-1241265453-1002 |
| ローカルユーザー | WDAGUtilityAccount | S-1-5-21-2751499492-1868010712-940411855-504 | S-1-5-21-1010608215-2051037059-1241265453-504 |
| ローカルグループ | Access-Denied Assistance Users | S-1-5-21-2751499492-1868010712-940411855-1000 | S-1-5-21-1010608215-2051037059-1241265453-1003 |
| ローカルグループ | GitlabAdmin | S-1-5-21-2751499492-1868010712-940411855-1002 | S-1-5-21-1010608215-2051037059-1241265453-1001 |
| ローカルグループ | GrSpecialAccount01 | S-1-5-21-2751499492-1868010712-940411855-1001 | S-1-5-21-1010608215-2051037059-1241265453-1000 |

##### 2. ACLの保存

最終差分コピーの前に、旧サーバーでACLをファイルへ保存する。ACL保存ファイル自身が `D:\ENG\*` の保存対象に入らないよう、いったん `$env:TEMP` に保存し、完了後に `D:\ENG\AclBackup` へ移動する。既存ファイルへの保存を避け、処理件数を確認できるよう `/Q` は付けない。

```powershell
$aclDirectory = "D:\ENG\AclBackup"
$aclFile = Join-Path $aclDirectory "acl-before-migration.txt"
$temporaryAclFile = Join-Path $env:TEMP "acl-before-migration.txt"
New-Item -ItemType Directory -Path $aclDirectory -Force | Out-Null
if (Test-Path -LiteralPath $aclFile) {
    throw "ACL保存先が既に存在します。削除するか別名を指定してください: $aclFile"
}
if (Test-Path -LiteralPath $temporaryAclFile) {
    throw "一時ACL保存先が既に存在します。削除するか別名を指定してください: $temporaryAclFile"
}
icacls.exe "D:\ENG\*" /save $temporaryAclFile /T /C
if ($LASTEXITCODE -ne 0 -or (Get-Item -LiteralPath $temporaryAclFile).Length -eq 0) {
    throw "ACLの保存に失敗したか、ACLファイルが空です。"
}
Move-Item -LiteralPath $temporaryAclFile -Destination $aclFile
```

正常に処理されたファイル数が1件以上、処理できなかったファイル数が0件であることを確認してから、新サーバーへコピーする。

新サーバーで、旧サーバーの管理共有からACLファイルを取得する。

```powershell
New-Item -ItemType Directory -Path "D:\ENG\AclBackup" -Force | Out-Null
Copy-Item "\\192.168.2.210\D$\ENG\AclBackup\acl-before-migration.txt" "D:\ENG\AclBackup\acl-before-migration.txt"
```

新サーバーの `D:\ENG\AclBackup\acl-before-migration.txt` にファイルが存在することを確認する。

##### 3. ACLファイル内のSIDの置換と復元

最終差分コピーが完了した後、新サーバーでACL保存ファイルのコピーを作り、そのコピー内の旧SIDを新SIDへ置換する。`icacls /substitute` は、旧サーバーのローカルSIDを解決できずエラー1332になるため使用しない。元の `acl-before-migration.txt` はロールバック用として変更せずに保持する。

```powershell
$source = "D:\ENG\AclBackup\acl-before-migration.txt"
$output = "D:\ENG\AclBackup\acl-before-migration-converted.txt"

if (Test-Path -LiteralPath $output) {
    throw "変換後ACLファイルが既に存在します: $output"
}

$sidMap = [ordered]@{
    "S-1-5-21-2751499492-1868010712-940411855-500"  = "S-1-5-21-1010608215-2051037059-1241265453-500"
    "S-1-5-21-2751499492-1868010712-940411855-503"  = "S-1-5-21-1010608215-2051037059-1241265453-503"
    "S-1-5-21-2751499492-1868010712-940411855-501"  = "S-1-5-21-1010608215-2051037059-1241265453-501"
    "S-1-5-21-2751499492-1868010712-940411855-1003" = "S-1-5-21-1010608215-2051037059-1241265453-1002"
    "S-1-5-21-2751499492-1868010712-940411855-504"  = "S-1-5-21-1010608215-2051037059-1241265453-504"
    "S-1-5-21-2751499492-1868010712-940411855-1000" = "S-1-5-21-1010608215-2051037059-1241265453-1003"
    "S-1-5-21-2751499492-1868010712-940411855-1002" = "S-1-5-21-1010608215-2051037059-1241265453-1001"
    "S-1-5-21-2751499492-1868010712-940411855-1001" = "S-1-5-21-1010608215-2051037059-1241265453-1000"
}

# ACLファイルが大きくなる可能性があるため、1行ずつ変換する。
$counts = @{}
foreach ($oldSid in $sidMap.Keys) { $counts[$oldSid] = 0 }
$encoding = [System.Text.UnicodeEncoding]::new($false, $true)
$reader = [System.IO.StreamReader]::new($source, [System.Text.Encoding]::Unicode, $true)
$writer = [System.IO.StreamWriter]::new($output, $false, $encoding)
try {
    while (($line = $reader.ReadLine()) -ne $null) {
        foreach ($oldSid in $sidMap.Keys) {
            $counts[$oldSid] += ([regex]::Matches($line, [regex]::Escape($oldSid))).Count
            $line = $line.Replace($oldSid, $sidMap[$oldSid])
        }
        $writer.WriteLine($line)
    }
}
finally {
    $reader.Dispose()
    $writer.Dispose()
}
$counts.GetEnumerator() | Sort-Object Name | Format-Table Name, Value -AutoSize

if (Select-String -LiteralPath $output -Pattern ([char]0) -SimpleMatch -Quiet -Encoding Unicode) {
    throw "変換後ACLファイルにNUL文字が含まれています。復元しないでください。"
}
if (Select-String -LiteralPath $output -Pattern @($sidMap.Keys) -SimpleMatch -Quiet -Encoding Unicode) {
    throw "変換後ACLファイルに置換対象の旧SIDが残っています。復元しないでください。"
}
```

表示されたSIDごとの置換件数を確認する。また、次のコマンドでファイル名とSDDLが文字間の空白なしで表示されることを確認してから、変換後のACLファイルを復元する。

```powershell
Get-Content -LiteralPath $output -Encoding Unicode -TotalCount 4
```

```powershell
icacls.exe "D:\ENG" /restore "D:\ENG\AclBackup\acl-before-migration-converted.txt" /C
```

SID置換後にRobocopyを `/COPYALL` 付きで再実行すると旧SIDが再設定される可能性があるため、以後Robocopyを実行した場合は、ACLファイルの変換と復元も再実行する。

##### 4. 確認

1. `icacls` の実行結果で処理失敗がないことを確認する。
1. 新サーバーのファイルまたはフォルダーの「セキュリティ」タブを開き、「不明なアカウント」が残っていないことを確認する。
1. 新サーバーのローカルユーザーまたはローカルグループに、旧サーバーと同等のアクセス許可が設定されていることを確認する。
1. 対象ユーザーでファイルの読み取り、作成、更新をテストする。

`icacls /save` および `/restore` の対象はDACLである。所有者または監査情報に旧ローカルSIDが使用されている場合は、別途確認して再設定する。


## テスト

### ファイル移行の確認

1. 各Robocopyログについて、終了コードが0から7であり、失敗（`FAILED`）が0件であることを確認する。
1. コピー元とコピー先のファイル数、フォルダー数および容量を比較する。
1. 日本語名、長い名前、大容量ファイルを含む代表的なファイルを開けることを確認する。
1. 代表的な共有について、読み取り、作成、更新、削除を許可されたユーザーでテストする。
1. 許可されていないユーザーがアクセスできないことを確認する。
1. ファイルとフォルダーの「セキュリティ」タブまたは `icacls` で、旧サーバーのSIDが「不明なアカウント」として残っていないことを確認する。

### Gitリポジトリの整合性確認

移行前後の各Gitリポジトリで次を実行し、結果を比較する。

```powershell
git -C "リポジトリのパス" fsck --no-dangling
git -C "リポジトリのパス" status --porcelain=v1
git -C "リポジトリのパス" rev-parse HEAD
git -C "リポジトリのパス" for-each-ref --format="%(refname) %(objectname)"
git -C "リポジトリのパス" count-objects -vH
```

次を合格条件とする。

1. `git fsck` で破損エラーが発生しない。
1. HEADのコミットIDが移行前後で一致する。
1. ブランチ、タグおよびそれぞれの参照先コミットIDが一致する。
1. 未コミットファイルの状態が一致する。
1. clone、checkout、履歴表示が成功する。

### GitLabの機能確認

専用のテストリポジトリを使用して次を確認する。

1. Web画面でプロジェクト、コミットおよび差分を表示できる。
1. HTTPSまたはSSHでcloneできる。
1. テストブランチを作成してpush、fetchおよびpullができる。
1. テスト用のMerge Requestを作成できる。
1. Wiki、Git LFSまたはSubmoduleを使用している場合は、それぞれ参照できる。
1. CI/CDを使用している場合は、テストPipelineが正常終了する。
1. テスト完了後にテストブランチを削除できる。

### RAGデータの整合性確認

移行前後で次を比較する。

1. コレクションまたはインデックスの名前と数
1. 元文書数、チャンク数およびベクトル数
1. ベクトルの次元数
1. 埋め込みモデルの名前とバージョン
1. コサイン類似度などの距離計算方式
1. 文書IDとチャンクIDの対応
1. 最終更新日時

文書数、チャンク数およびベクトル数が一致し、参照先文書のないベクトルや、ベクトル化されていない対象チャンクがないことを合格条件とする。

ベクトルデータベースがPostgreSQL/pgvector、Qdrant、MilvusまたはElasticsearchなどの場合は、稼働中のデータファイルをRobocopyせず、製品固有のバックアップまたはスナップショット機能を使用する。

### RAG検索の再現確認

業務上代表的な質問を20件から50件用意し、移行前後で同じ検索を実行する。質問ごとに次を記録して比較する。

1. 上位10件の文書IDとチャンクID
1. 類似度スコア
1. 生成された回答
1. 回答の引用元
1. 応答時間

主要な上位文書と引用元が移行前後で一致し、引用元ファイルを実際に開けることを確認する。日本語の質問、日本語ファイル名および表記揺れを含む質問も使用する。検索結果の順位や類似度スコアに許容差を設ける場合は、テスト前に基準を決める。

### テスト不調時のロールバック

1. 不調が発覚
1. 新サーバのIPアドレス、ホスト名を192.168.2.152　NTSRV-ENGNに変更し、再起動
1. （再起動完了後）旧サーバの電源ON（vCenterから起動）
