---
layout: page
title: "Tags"
description: "Keywords"
header-img: "img/bkstone.jpg"  
---

<div id='tag_cloud' class="tags">
    {% for tag in site.tags %}
    <a href="#{{ tag[0] }}" title="{{ tag[0] }}" rel="{{ tag[1].size }}">{{ tag[0] }}</a>
    {% endfor %}
</div>

<!-- 标签列表 -->
{% for tag in site.tags %}
<div class="one-tag-list">
    <span class="fa fa-tag listing-seperator" id="{{ tag[0] }}">
        <span class="tag-text">{{ tag[0] }}</span>
    </span>
    {% for post in tag[1] %}
        <li class="listing-item">
        <time datetime="{{ post.date | date:"%Y-%m-%d" }}">{{ post.date | date:"%Y-%m-%d" }}</time>
        <a href="{{ post.url }}" title="{{ post.title }}">{{ post.title }}</a>
        </li>
    <div class="post-preview">
        <a href="{{ post.url | prepend: site.baseurl }}">
            <h3 class="post-title">
                {{ post.title }}
            </h3>
            {% if post.subtitle %}
            <h4 class="post-subtitle">
                {{ post.subtitle }}
            </h4>
            {% endif %}
        </a>
        <!-- <p class="post-meta">{{ post.date | date:"%Y-%m-%d" }}</p> -->
    </div>
    <hr>
    {% endfor %}
</div>
{% endfor %}

