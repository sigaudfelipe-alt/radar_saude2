"""Render a WeeklyNewsletter into human-readable formats.

This module uses Jinja2 to convert the structured WeeklyNewsletter data
into Markdown. The resulting Markdown can be sent directly in emails or
converted to HTML if desired. Rendering is separated to allow easy
customisation of the newsletter template.
"""

from datetime import datetime, timezone
from pathlib import Path

from jinja2 import Template  # type: ignore

from .data_model import WeeklyNewsletter


NEWSLETTER_MD_TEMPLATE = """
[RADAR SAÚDE | {{ newsletter.periodo_label }} ]

1. O QUE IMPORTA ESTA SEMANA
{% for b in newsletter.bullets_top3 %}
- {{ b }}
{% endfor %}

--------------------------------------------------
2. PANORAMA SAÚDE
2.1 Brasil
{% for n in newsletter.panorama_brasil %}
• {{ n.titulo }} – {{ n.fonte }}, {{ n.data_publicacao.strftime('%d/%m/%Y') }}
  - {{ n.resumo_exec }}
{% endfor %}

2.2 Internacional
{% for n in newsletter.panorama_global %}
• {{ n.titulo }} – {{ n.fonte }}, {{ n.data_publicacao.strftime('%d/%m/%Y') }}
  - {{ n.resumo_exec }}
{% endfor %}

--------------------------------------------------
3. SAÚDE DIGITAL & MODELOS DE CUIDADO
{% for n in newsletter.saude_digital %}
• {{ n.titulo }} – {{ n.fonte }}
  - {{ n.resumo_exec }}
  - Link: {{ n.url }}
{% endfor %}

--------------------------------------------------
4. TECNOLOGIA EM SAÚDE / IA / PRODUTO
{% for n in newsletter.tech_saude %}
• {{ n.titulo }} – {{ n.fonte }}
  - {{ n.resumo_exec }}
  - Link: {{ n.url }}
{% endfor %}

--------------------------------------------------
5. DEALS DA SEMANA
BRASIL / LATAM
{% for d in newsletter.deals_brasil %}
- Alvo: {{ d.alvo }} | Comprador/Investidor: {{ d.comprador_investidor }} | Valor: {{ d.valor }}
  Tese: {{ d.tese }}
{% endfor %}

GLOBAL
{% for d in newsletter.deals_global %}
- Alvo: {{ d.alvo }} | Comprador/Investidor: {{ d.comprador_investidor }} | Valor: {{ d.valor }}
  Tese: {{ d.tese }}
{% endfor %}

--------------------------------------------------
6. CONEXA NA SEMANA
{% for c in newsletter.conexa_blocos %}
{{ c }}

{% endfor %}

--------------------------------------------------
7. AGENDA E PRÓXIMOS GATILHOS
{% for a in newsletter.agenda_itens %}
- {{ a }}
{% endfor %}

--------------------------------------------------
FECHANDO
{{ newsletter.fechamento }}
"""


def render_markdown(newsletter: WeeklyNewsletter) -> str:
    """Render the newsletter into Markdown using Jinja2."""
    tpl = Template(NEWSLETTER_MD_TEMPLATE)
    return tpl.render(newsletter=newsletter)


def save_outputs(newsletter_md: str) -> str:
    """Persist the rendered Markdown to the output directory.

    Returns the path to the saved file for further processing (e.g., email).
    """
    out_dir = Path("output")
    out_dir.mkdir(exist_ok=True)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    md_path = out_dir / f"newsletter-{now}.md"
    md_path.write_text(newsletter_md, encoding="utf-8")
    return str(md_path)


if __name__ == "__main__":
    # Generate a dummy newsletter for testing purposes.
    from .data_model import WeeklyNewsletter

    dummy = WeeklyNewsletter(
        periodo_label="Semana de 20/10/2025 a 27/10/2025",
        bullets_top3=["Exemplo bullet 1", "Exemplo bullet 2", "Exemplo bullet 3"],
        panorama_brasil=[],
        panorama_global=[],
        saude_digital=[],
        tech_saude=[],
        deals_brasil=[],
        deals_global=[],
        conexa_blocos=["Conexa firmou parceria X para coordenação de cuidado."],
        agenda_itens=["ANS discute telessaúde corporativa."],
        fechamento="Modelos digitais viraram ferramenta financeira.",
    )
    md_text = render_markdown(dummy)
    path = save_outputs(md_text)
    print(f"Arquivo de teste gerado em {path}")