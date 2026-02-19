---
layout: default
title: Home
---

<header class="hero">
  <div class="hero__content container">
    <div class="hero-grid">
      <div>
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
      <figure class="profile-frame">
        <img src="{{ '/assets/profil.webp' | relative_url }}" alt="Portrait of {{ site.author.name }}" width="100" height="133">
      </figure>
    </div>
  </div>
</header>

<main class="container main-grid">
  <section>
    <div class="section-header">
      <h2>Publications</h2>
      <p class="muted">
        Last update:
        {% if site.data.publications.generated_at %}
          {{ site.data.publications.generated_at | date: "%Y-%m-%d" }}
        {% else %}
          not yet synced
        {% endif %}
      </p>
    </div>

    {% assign pubs = site.data.publications.items | sort: "year" | reverse %}
    {% assign pub_groups = pubs | group_by: "year" %}
    {% if pubs and pubs.size > 0 %}
      <div class="pub-groups">
        {% for group in pub_groups %}
          <div class="year-block">
            <h3 class="year-heading">{{ group.name }}</h3>
            <div class="pub-list">
              {% for pub in group.items %}
          {% assign authors_raw = pub.authors | default: "Unknown authors" %}
          {% assign author_list = authors_raw | split: " and " %}
          {% capture authors %}{% for author in author_list %}{% if forloop.first %}{{ author }}{% elsif forloop.last %} and {{ author }}{% else %}, {{ author }}{% endif %}{% endfor %}{% endcapture %}
          {% assign authors = authors | strip %}
          {% assign authors = authors
            | replace: "Winfried Lötzsch", "<span class='author-highlight'>Winfried Lötzsch</span>"
            | replace: "Winfried Loetzsch", "<span class='author-highlight'>Winfried Loetzsch</span>"
            | replace: "Winfried Ripken", "<span class='author-highlight'>Winfried Ripken</span>"
          %}

              <article class="pub-item">
                <h4 class="pub-title">
              {% if pub.url %}
                <a href="{{ pub.url }}">{{ pub.title }}</a>
              {% else %}
                {{ pub.title }}
              {% endif %}
                </h4>
                <p class="pub-authors">{{ authors }}</p>
                <p class="pub-venue">{{ pub.venue | default: "Unknown venue" }}:</p>
                <p class="pub-cites">Citations: {{ pub.citations | default: 0 }}</p>
              </article>
              {% endfor %}
            </div>
          </div>
        {% endfor %}
      </div>
    {% else %}
      <p>No publications synced yet. Run the workflow once from the Actions tab.</p>
    {% endif %}
  </section>
</main>
