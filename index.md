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
        <img src="{{ '/assets/profil.webp' | relative_url }}" alt="Portrait of {{ site.author.name }}">
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
          {{ site.data.publications.generated_at }}
        {% else %}
          not yet synced
        {% endif %}
      </p>
    </div>

    {% assign pubs = site.data.publications.items | sort: "year" | reverse %}
    {% if pubs and pubs.size > 0 %}
      <div class="pub-list">
        {% assign current_year = "" %}
        {% for pub in pubs %}
          {% assign pub_year = pub.year | default: 0 %}
          {% if pub_year != current_year %}
            {% assign current_year = pub_year %}
            <h3 class="year-heading">{{ current_year }}</h3>
          {% endif %}

          {% assign authors = pub.authors | default: "Unknown authors" %}
          {% assign authors = authors
            | replace: "Winfried Lötzsch", "<span class='author-highlight'>Winfried Lötzsch</span>"
            | replace: "Winfried Loetzsch", "<span class='author-highlight'>Winfried Loetzsch</span>"
            | replace: "Winfried Ripken", "<span class='author-highlight'>Winfried Ripken</span>"
          %}

          <article class="pub-item">
            <p class="pub-authors">{{ authors }}</p>
            <h4 class="pub-title">
              {% if pub.url %}
                <a href="{{ pub.url }}">{{ pub.title }}</a>
              {% else %}
                {{ pub.title }}
              {% endif %}
            </h4>
            <div class="pub-meta-grid">
              <p><span class="meta-label">Venue</span> {{ pub.venue | default: "Unknown venue" }}</p>
              <p><span class="meta-label">Year</span> {{ pub_year }}</p>
              <p><span class="meta-label">Citations</span> {{ pub.citations | default: 0 }}</p>
            </div>
          </article>
        {% endfor %}
      </div>
    {% else %}
      <p>No publications synced yet. Run the workflow once from the Actions tab.</p>
    {% endif %}
  </section>
</main>
