# kaggle-template

- Template directory for datascience competitions.
- Data is saved in PostgreSQL on Docker🐳 container and the data is reproducibule/reusable 😄🎉

## Usage

### Step0. Clone the repository

```sh
git clone https://github.com/kiccho1101/kaggle-base.git
cd kaggle-base
```

### Step1. Pull/Build Docker image

Recommended:

```sh
make pull
```

or

```sh
make build
```

### Step2. Start up jupyter notebook

```sh
make jupyter
```

- Copy token and acccess to localhost:${JUPYTER_PORT} (default: 9000)

### Step3. Start up DB

```sh
make start-db
```

- Then you can access to localhost:${PGWEB_PORT} (default: 9002) to view the database.

### Step4. Split train data into K-fold

```sh
make kfold CONFIG_NAME(default: lightgbm_0)
```

### Step5. Create Features

- Create all features.

```sh
make feature
```

- Specify a feature that will be created.

```sh
make feature FEATURE_NAME
```

### Step6. Cross Validation

```sh
make cv CONFIG_NAME
```

### Step7. Create Stats of each table

```sh
make stats
```

### Step8. Train and Predict

```sh
make train-and-predict CONFIG_NAME
```

### Step9. Submit

- Then submit your output file!🙆

```sh
./output/submission_xxx.csv
```

## Commands

### isort, black

```sh
make format
```

### flake8, mypy

```sh
make check
```

### Reset DB

```sh
make reset-db
```

### execute scripts

Recommended:

```sh
make shell
python xxx.py
```

or

```sh
make run python xxx.py
```

## References

### [1.データ分析コンペにおいて 特徴量管理に疲弊している全人類に伝えたい想い][1]

まさに特徴量管理に疲弊していたときに見つけたスライド。すごくわかりやすいです。

### [2.Kaggleで使えるFeather形式を利用した特徴量管理法][2]

クラスの書き方が参考になります。

### [3.flowlight0's directory][3]

Featureクラスの継承が、すごく参考になりました

### [4.upura's directory][4]

このディレクトリを作ろうと思ったきっかけになったディレクトリ。参考になります。

[1]:https://speakerdeck.com/takapy/detafen-xi-konpenioite-te-zheng-liang-guan-li-nipi-bi-siteiruquan-ren-lei-nichuan-etaixiang-i
[2]:https://amalog.hateblo.jp/entry/kaggle-feature-management
[3]:https://github.com/flowlight0/talkingdata-adtracking-fraud-detection
[4]:https://github.com/upura/ml-competition-template-titanic
