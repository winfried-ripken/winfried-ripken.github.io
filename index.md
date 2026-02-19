---
layout: default
title: Home
---

<header class="hero">
  <div class="hero__content container">
    <p class="eyebrow">Academic Website</p>
    <h1>{{ site.author.name }}</h1>
    <p class="subtitle">{{ site.author.role }} · {{ site.author.affiliation }}</p>
    <p class="lead">
      I am a PhD student within the <a href="https://www.bifold.berlin/research/workgroups/view/workgroups-detail/machine-learning-for-molecular-simulation-in-quantum-chemistry">BIFOLD graduate school</a> advised by Stefan Chmiela and Klaus-Robert Müller. I am passionate about applying advances in machine learning to problems in the natural sciences, especially for molecular simulation.
      Before this, I worked as a full-time machine learning researcher at
      <a href="https://merantix-momentum.com/">Merantix Momentum</a>.
    </p>
    <div class="cta-row">
      <a class="button" href="{{ site.author.scholar_url }}">Google Scholar</a>
      <a class="button button--ghost" href="https://github.com/{{ site.author.github }}">GitHub</a>
      {% if site.author.twitter %}
      <a class="button button--ghost" href="https://x.com/{{ site.author.twitter }}">X/Twitter</a>
      {% endif %}
    </div>
  </div>
</header>

<main class="container main-grid">
  <section>
    <h2>About</h2>
    <p>
      This site is optimized for an up-to-date publication list. Publications are fetched from Google Scholar
      on a schedule via GitHub Actions and rendered automatically.
    </p>
  </section>

  <section>
    <div class="section-header">
      <h2>Publications</h2>
      <p class="muted">
        Last update:
        {% if site.data.publications.generated_at %}
          {{ site.data.publications.generated_at }}
        {% else %}
          not yet synced
        {% endif %}
      </p>
    </div>

    {% assign pubs = site.data.publications.items %}
    {% if pubs and pubs.size > 0 %}
      <ol class="pub-list">
        {% for pub in pubs %}
          <li class="pub-item">
            <h3>
              {% if pub.url %}
                <a href="{{ pub.url }}">{{ pub.title }}</a>
              {% else %}
                {{ pub.title }}
              {% endif %}
            </h3>
            <p class="pub-meta">{{ pub.authors }} · {{ pub.venue }} · {{ pub.year }}</p>
            {% if pub.citations %}<p class="pub-cites">Citations: {{ pub.citations }}</p>{% endif %}
          </li>
        {% endfor %}
      </ol>
    {% else %}
      <p>No publications synced yet. Run the workflow once from the Actions tab.</p>
    {% endif %}
  </section>
</main>
