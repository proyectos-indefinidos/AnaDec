import Link from "next/link";

import Button from "@/components/ui/Button";
import Card from "@/components/ui/Card";
import SectionTitle from "@/components/ui/SectionTitle";

const quickAccess = [
  {
    title: "Convertidor",
    description: "Pasa una tasa de un periodo a otro en segundos.",
    href: "/convertidor",
  },
  {
    title: "Comparador",
    description: "Compara dos opciones y mira cual te conviene mas.",
    href: "/comparador",
  },
  {
    title: "Noticias",
    description: "Revisa novedades economicas para tomar mejores decisiones.",
    href: "/noticias",
  },
];

export default function HomePage() {
  return (
    <section className="space-y-10">
      <Card className="p-8 md:p-10">
        <SectionTitle
          title="Convierte y compara tasas facilmente"
          subtitle="Entiende cuanto estas pagando o ganando sin formulas complicadas."
        />

        <div className="mt-6 flex flex-wrap gap-3">
          <Link href="/convertidor">
            <Button variant="primary">Ir a convertidor</Button>
          </Link>
          <Link href="/comparador">
            <Button variant="secondary">Ir a comparador</Button>
          </Link>
        </div>
      </Card>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
        {quickAccess.map((item) => (
          <Card key={item.title}>
            <div className="space-y-4">
              <SectionTitle title={item.title} subtitle={item.description} />
              <Link href={item.href}>
                <Button variant="secondary">Ir</Button>
              </Link>
            </div>
          </Card>
        ))}
      </div>
    </section>
  );
}
