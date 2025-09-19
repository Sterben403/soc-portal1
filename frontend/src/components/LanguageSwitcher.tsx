import { useTranslation } from "react-i18next";
import { useMemo } from "react";

type Props = {
  floating?: boolean; // если true — рисуем компактный переключатель, закреплённый сверху-справа
};

const LANGS = [
  { code: "en", label: "EN" },
  { code: "ru", label: "RU" },
  { code: "kk", label: "KK" },
];

export default function LanguageSwitcher({ floating = true }: Props) {
  const { i18n } = useTranslation();

  const value = useMemo(() => {
    const cur = i18n.language?.slice(0, 2).toLowerCase();
    return LANGS.find(l => l.code === cur)?.code ?? "en";
  }, [i18n.language]);

  return (
    <div
      className={floating ? "lang-switcher-floating" : ""}
      title="Language"
    >
      <select
        aria-label="Select language"
        className="lang-switcher-select"
        value={value}
        onChange={(e) => i18n.changeLanguage(e.target.value)}
      >
        {LANGS.map(l => (
          <option key={l.code} value={l.code}>{l.label}</option>
        ))}
      </select>
    </div>
  );
}
