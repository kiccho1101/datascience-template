# kaggle-template

- Template directory for datascience competitions.
- Data is stored in PostgreSQL on Docker🐳 container and the data is reproducibule/reusable 😄🎉

## Usage

### Step0. Clone the repository

```sh
git clone git@github.com:kiccho1101/kaggle-template.git
cd kaggle-template
```

### Step1. Download train.csv and test.csv into ./input folder

Download them from [https://www.kaggle.com/c/titanic](https://www.kaggle.com/c/titanic)

### Step2. Run the init.sh

All you have to do is just run the init.sh.
It will do pretty much everything for you! 🎉

```bash
sh init.sh
```

### Step3. Split tables into K-Fold

```sh
make kfold {CONFIG_NAME}

# Example
make kfold basic
```

### Step4. Cross Validation

```sh
make cv {EXP_NAME}

# Example
make cv exp1
```

### Step5. Create submit file

```sh
make predict {EXP_NAME}

# Example
make predict exp1
```

## Utilities

### Open pgweb

```sh
docker-compose up -d pgweb
make pgweb
```

### Open jupyter notebook

```sh
make jupyter
```

### Run Python script

```sh
make run python xxx.py
```

### Format

```sh
make format
```

## References

### [1.データ分析コンペにおいて 特徴量管理に疲弊している全人類に伝えたい想い][1]

まさに特徴量管理に疲弊していたときに見つけたスライド。すごくわかりやすいです。

### [2.Kaggleで使えるFeather形式を利用した特徴量管理法][2]

クラスの書き方でかなり参考にさせていただきました。

### [3.github.com/upura/ml-competition-template-titanic][3]

このディレクトリを作ろうと思ったきっかけになったディレクトリ。

[1]:https://speakerdeck.com/takapy/detafen-xi-konpenioite-te-zheng-liang-guan-li-nipi-bi-siteiruquan-ren-lei-nichuan-etaixiang-i
[2]:https://amalog.hateblo.jp/entry/kaggle-feature-management
[3]:https://github.com/upura/ml-competition-template-titanic
