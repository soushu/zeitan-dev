import Link from "next/link";

export function LandingHero() {
  return (
    <section className="relative overflow-hidden bg-gradient-to-br from-slate-50 via-white to-blue-50 py-20 sm:py-32">
      <div className="mx-auto max-w-6xl px-4 sm:px-6">
        <div className="max-w-3xl">
          <div className="inline-flex items-center gap-2 rounded-full bg-blue-50 border border-blue-200 px-3 py-1 text-xs font-medium text-blue-700 mb-6">
            国内外70以上の取引所に対応
          </div>
          <h1 className="text-3xl sm:text-5xl font-bold tracking-tight text-slate-900 leading-tight">
            暗号資産の税金計算を
            <br />
            <span className="text-blue-600">シンプル</span>に。
          </h1>
          <p className="mt-6 text-base sm:text-lg text-slate-600 max-w-2xl leading-relaxed">
            CSVをアップロードするだけで、移動平均法・総平均法による損益計算を自動実行。
            確定申告に必要なレポートもワンクリックで作成できます。
          </p>
          <div className="mt-8 flex flex-col sm:flex-row gap-3">
            <Link
              href="/login"
              className="inline-flex items-center justify-center rounded-lg bg-slate-900 px-6 py-3 text-base font-semibold text-white hover:bg-slate-800 transition-colors"
            >
              無料で始める
            </Link>
            <a
              href="#features"
              className="inline-flex items-center justify-center rounded-lg border border-slate-300 bg-white px-6 py-3 text-base font-semibold text-slate-700 hover:bg-slate-50 transition-colors"
            >
              機能を見る
            </a>
          </div>
        </div>
      </div>
      {/* Decorative background */}
      <div className="absolute top-0 right-0 -z-10 w-1/2 h-full opacity-30">
        <div className="absolute inset-0 bg-gradient-to-l from-blue-100 to-transparent" />
      </div>
    </section>
  );
}
