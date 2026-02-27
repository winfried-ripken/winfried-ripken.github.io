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
          I am a PhD student within the <a href="https://www.bifold.berlin/people/winfried-ripken.html">BIFOLD graduate school</a> advised by Stefan Chmiela and Klaus-Robert Müller. I am passionate about applying advances in machine learning to problems in the natural sciences, especially for molecular simulation.
          Before this, I worked as a full-time machine learning researcher at
          <a href="https://merantix-momentum.com/">Merantix Momentum</a>.
        </p>
        <div class="cta-row">
          <a class="button" href="{{ site.author.scholar_url }}">Google Scholar</a>
          <a class="button button--ghost" href="{{ '/assets/CV_Ripken.pdf' | relative_url }}" target="_blank" rel="noopener noreferrer">CV (PDF)</a>
          <a class="button button--ghost" id="email-link" href="#" data-user-b64="d2luZnJpZWQucmlwa2Vu" data-domain-b64="Z21haWwuY29t">Email</a>
          <a class="button button--ghost" href="https://github.com/{{ site.author.github }}">GitHub</a>
          {% if site.author.twitter %}
          <a class="button button--ghost" href="https://x.com/{{ site.author.twitter }}">X/Twitter</a>
          {% endif %}
          {% if site.author.linkedin %}
          <a class="button button--ghost" href="{{ site.author.linkedin }}">LinkedIn</a>
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
      <div class="pub-filters">
        <label class="filter-field" for="year-filter">
          <span>Year</span>
          <select id="year-filter">
            <option value="">All years</option>
            {% for group in pub_groups %}
              <option value="{{ group.name }}">{{ group.name }}</option>
            {% endfor %}
          </select>
        </label>
        <label class="filter-field filter-field--search" for="text-filter">
          <span>Search</span>
          <input id="text-filter" type="search" placeholder="Title, authors, venue">
        </label>
      </div>
      <p id="pub-filter-empty" class="muted" hidden>No publications match the current filter.</p>
      <div class="pub-groups">
        {% for group in pub_groups %}
          <div class="year-block" data-year="{{ group.name }}">
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
                <p class="pub-venue">{{ pub.venue | default: "Unknown venue" }}</p>
                <!-- <p class="pub-cites">{{ pub.citations | default: 0 }} citations</p> -->
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

<script>
  document.addEventListener("DOMContentLoaded", function () {
    var emailLink = document.getElementById("email-link");
    var yearFilter = document.getElementById("year-filter");
    var textFilter = document.getElementById("text-filter");
    var emptyState = document.getElementById("pub-filter-empty");
    var groups = document.querySelectorAll(".year-block");

    if (emailLink) {
      var user = atob(emailLink.dataset.userB64 || "");
      var domain = atob(emailLink.dataset.domainB64 || "");
      if (user && domain) {
        emailLink.href = "mailto:" + user + "@" + domain;
      } else {
        emailLink.remove();
      }
    }

    if (!yearFilter || !textFilter || !groups.length) {
      return;
    }

    function applyFilters() {
      var selectedYear = yearFilter.value.trim();
      var query = textFilter.value.trim().toLowerCase();
      var anyVisible = false;

      groups.forEach(function (group) {
        var groupYear = (group.dataset.year || "").trim();
        var yearMatches = !selectedYear || groupYear === selectedYear;
        var cards = group.querySelectorAll(".pub-item");
        var visibleInGroup = 0;

        cards.forEach(function (card) {
          var haystack = card.textContent.toLowerCase();
          var textMatches = !query || haystack.indexOf(query) !== -1;
          var show = yearMatches && textMatches;
          card.hidden = !show;
          if (show) {
            visibleInGroup += 1;
            anyVisible = true;
          }
        });

        group.hidden = visibleInGroup === 0;
      });

      if (emptyState) {
        emptyState.hidden = anyVisible;
      }
    }

    yearFilter.addEventListener("change", applyFilters);
    textFilter.addEventListener("input", applyFilters);
  });
</script>
