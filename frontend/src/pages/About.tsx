import { useTranslation } from "react-i18next";

const TEAM = ["Trần Thị Thùy Dương", "Lê Thái Lâm", "Phạm Lan Nhi"];
const CITATIONS = [
  "Dou et al., User Preference-aware Fake News Detection, SIGIR 2021 (UPFD).",
  "Shu et al., FakeNewsNet, Big Data 2020.",
  "Bian et al., Rumor Detection on Social Media with Bi-Directional Graph Convolutional Networks, AAAI 2020.",
  "PyTorch Geometric: torch_geometric.datasets.UPFD.",
];

export default function About() {
  const { t } = useTranslation();
  const does = t("about.does", { returnObjects: true }) as string[];
  const doesNot = t("about.doesNot", { returnObjects: true }) as string[];
  const questions = t("about.questions", { returnObjects: true }) as string[];

  return (
    <article className="prose">
      <h1>{t("about.title")}</h1>
      <p className="lead">{t("about.lead")}</p>

      <h2>{t("about.methodTitle")}</h2>
      <p>{t("about.method")}</p>
      <ol>
        {questions.map((q) => (
          <li key={q}>{q}</li>
        ))}
      </ol>

      <h2>{t("about.scopeTitle")}</h2>
      <div className="two-col">
        <div>
          <h3>{t("about.doesTitle")}</h3>
          <ul>
            {does.map((x) => (
              <li key={x}>{x}</li>
            ))}
          </ul>
        </div>
        <div>
          <h3>{t("about.doesNotTitle")}</h3>
          <ul>
            {doesNot.map((x) => (
              <li key={x}>{x}</li>
            ))}
          </ul>
        </div>
      </div>

      <h2>{t("about.teamTitle")}</h2>
      <p>{t("about.course")}</p>
      <p>{t("about.supervisor")}: PGS.TS. Nguyễn Thanh Bình</p>
      <ul>
        {TEAM.map((n) => (
          <li key={n}>{n}</li>
        ))}
      </ul>

      <h2>{t("about.citationsTitle")}</h2>
      <ul className="citations">
        {CITATIONS.map((c) => (
          <li key={c}>{c}</li>
        ))}
      </ul>

      <h2>{t("about.disclaimerTitle")}</h2>
      <p>{t("footer.disclaimer")}</p>
    </article>
  );
}
