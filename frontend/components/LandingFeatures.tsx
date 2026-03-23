const exchanges = [
  "BitFlyer", "Coincheck", "Binance", "GMO", "bitbank",
  "SBI VC", "Bybit", "Kraken", "Coinbase", "Rakuten",
];

const steps = [
  {
    number: "1",
    title: "CSVをアップロード",
    description: "取引所からダウンロードした取引履歴CSVをアップロード。複数の取引所に対応。",
  },
  {
    number: "2",
    title: "計算方法を選択",
    description: "移動平均法・総平均法から選択。ワンクリックで切り替えて比較も可能。",
  },
  {
    number: "3",
    title: "結果を確認",
    description: "損益計算結果を即座に確認。CSV・PDFレポートのダウンロードも可能。",
  },
];

const features = [
  {
    title: "移動平均法 / 総平均法",
    description: "2つの計算方法に対応。ワンクリックで切り替えて最適な方法を選べます。",
  },
  {
    title: "年度別フィルター",
    description: "年度ごとに計算履歴を絞り込み。過去の申告データもすぐに確認。",
  },
  {
    title: "ダッシュボード",
    description: "損益サマリー・月別推移・通貨別内訳をグラフで可視化。",
  },
  {
    title: "PDF / CSV レポート",
    description: "確定申告に使える損益計算レポートをワンクリックでダウンロード。",
  },
  {
    title: "要処理アラート",
    description: "売却超過や重複取引などの問題を自動検出してお知らせ。",
  },
  {
    title: "スマホ対応",
    description: "スマートフォンからでも快適に操作できるレスポンシブデザイン。",
  },
];

export function LandingFeatures() {
  return (
    <>
      {/* Exchanges */}
      <section className="border-y bg-slate-50 py-10">
        <div className="mx-auto max-w-6xl px-4 sm:px-6">
          <p className="text-center text-sm text-slate-500 mb-6">対応取引所</p>
          <div className="flex flex-wrap justify-center gap-4 sm:gap-8">
            {exchanges.map((name) => (
              <span key={name} className="text-sm sm:text-base font-medium text-slate-400">
                {name}
              </span>
            ))}
          </div>
        </div>
      </section>

      {/* 3 Steps */}
      <section className="py-16 sm:py-24" id="features">
        <div className="mx-auto max-w-6xl px-4 sm:px-6">
          <div className="text-center mb-12">
            <h2 className="text-2xl sm:text-3xl font-bold text-slate-900">
              確定申告まで簡単3ステップ
            </h2>
            <p className="mt-3 text-slate-500">
              面倒な損益計算を自動化。計算ミスの心配もありません。
            </p>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-8">
            {steps.map((step) => (
              <div key={step.number} className="text-center">
                <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-blue-100 text-blue-700 text-lg font-bold">
                  {step.number}
                </div>
                <h3 className="text-lg font-semibold text-slate-900 mb-2">
                  {step.title}
                </h3>
                <p className="text-sm text-slate-500 leading-relaxed">
                  {step.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Feature Grid */}
      <section className="bg-slate-50 py-16 sm:py-24">
        <div className="mx-auto max-w-6xl px-4 sm:px-6">
          <div className="text-center mb-12">
            <h2 className="text-2xl sm:text-3xl font-bold text-slate-900">
              主な機能
            </h2>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((feature) => (
              <div
                key={feature.title}
                className="rounded-xl border bg-white p-6 shadow-sm"
              >
                <h3 className="font-semibold text-slate-900 mb-2">
                  {feature.title}
                </h3>
                <p className="text-sm text-slate-500 leading-relaxed">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Free Plan */}
      <section className="py-16 sm:py-24">
        <div className="mx-auto max-w-3xl text-center px-4">
          <h2 className="text-2xl sm:text-3xl font-bold text-slate-900 mb-4">
            すべての機能を無料で利用可能
          </h2>
          <p className="text-slate-500 mb-8">
            現在、すべての機能を無料でご利用いただけます。
            <br />
            アカウント登録はメールアドレスのみで簡単に完了します。
          </p>
          <div className="inline-block rounded-2xl border-2 border-blue-200 bg-blue-50 px-8 py-6">
            <p className="text-sm font-medium text-blue-700 mb-1">フリープラン</p>
            <p className="text-4xl font-bold text-slate-900">
              &#165;0
              <span className="text-base font-normal text-slate-500">/月</span>
            </p>
            <p className="mt-2 text-sm text-slate-500">全機能利用可能</p>
          </div>
        </div>
      </section>
    </>
  );
}
