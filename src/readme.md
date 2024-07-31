# セットアップ
## 1. AWS SAMのインストール
- 手順: https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html

## 2. AWS CLIのインストール
- 手順: https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/prerequisites.html#prerequisites-install-cli
- AWSクレデンシャルを環境にエクスポートする
```bash
export AWS_ACCESS_KEY_ID=<value>
export AWS_SECRET_ACCESS_KEY=<value>
export AWS_DEFAULT_REGION=<value>
```


## 3. virtualenvのセットアップと依存関係のインストール
- virtualenvのセットアップと使用をお勧めします
```bash
# virtualenvのセットアップ
python3 -m virtualenv .venv
source .venv/bin/activate
```

## 4. SAMを使用してローカルでPricingCrawlerをテストする
- まず、`pricing`という名前のサブフォルダを持つ`S3 bucket`を作成する必要があります
- `global_settings.py` の設定を正しい値（`S3_PRICING_BUCKET_NAME`と`S3_PRICING_SUBDIR_PATH`）で更新してください
- この例では、`s3://mbs-for-test/pricing`とします
```
S3_PRICING_BUCKET_NAME = "mbs-for-test"
S3_PRICING_SUBDIR_PATH = "pricing/"
```

- フォルダが存在するか確認
```bash
aws s3 ls s3://mbs-for-test
# 出力
                           PRE pricing/
```

- ローカルで`PricingCrawl`を実行する
```bash
# 以下のコマンドを実行する前に src/PricingCrawler ディレクトリに移動してください
pip3 install -r requirements.txt
sam build

# jsonファイルを変更してどの商品を選択するか決める
sam local invoke PricingCrawler --event ./event_multi_sticker.json
#sam local invoke PricingCrawler --event ./event_seal.json
#sam local invoke PricingCrawler --event ./event_sticker.json
```

- 結果は以下のログに表示されるファイル名でS3にアップロードされます
```
Uploaded [pricing/printpac-multi-sticker_2024-07-31-05-54-53.json] successfully
```
- **このファイル名はPricingRegisterでテストする際に使用されます**


## 5. SAMを使用してローカルでPricingRegisterをテストする
- GoogleCloud Service-CloudのクレデンシャルをAWS SSMにアップロードします（JSONファイルの正しいパスを入力してください）
```bash
json_string=$(cat ~/Downloads/raksul-429806-fea1b10a1a87.json)
aws ssm put-parameter --name "/mbs-new-pricing/auth/bigquery" --value "$json_string" --type "String" --overwrite
```
** 注意: `/mbs-new-pricing/auth/bigquery`は名前に過ぎません。任意の値に変更することができます。
変更した場合、`PricingRegister/global_settings.py`内の変数`SSM_AUTH_PRM_KEY`に反映する必要があります。

- `PricingRegister/event_s3_upload.json`内のアップロードされたファイル名とS3バケット名を、ステップ4で使用したS3バケット名に変更する
- 必要に応じて、AWS S3（S3バケット）およびGoogle Bigquery（project_id、dataset）に関連する変数の値を変更する
- テストを実行する
```bash
# 以下のコマンドを実行する前にsrc/PricingRegisterディレクトリに移動してください
pip3 install -r requirements.txt
sam build
sam local invoke PricingRegister --event ./event_s3_upload.json
```
