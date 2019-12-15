# kaggle-template

- Template directory for datascience competitions.
- Data is saved in PostgreSQL on Docker🐳 container and the data is reproducibule/reusable 😄🎉

## Usage

### Step0. Clone the repository

```sh
git clone https://github.com/kiccho1101/kaggle-base.git
cd kaggle-base
```

### Step1. Run the init.sh

All you have to do is just run the init.sh.
It will do pretty much everything for you! 🎉

```bash
sh init.sh
```

### Step2. Copy jupyter token and access to it

```sh
make token
```

- Copy token and acccess to localhost:${JUPYTER_PORT} (default: 9000)

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
