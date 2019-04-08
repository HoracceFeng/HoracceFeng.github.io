---
layout: page
title: "Archive"
description: "藏书楼"
header-img: "img/stars.jpg"
---


<ul class="listing">
{% for post in site.posts %}
    {% capture y %}{{post.date | date:"%Y"}}{% endcapture %}
    {% if year != y %}
        {% assign year = y %}
        <!-- <li class="listing-seperator">{{ y }}</li> -->
        <p>{{ y }}</p>
    {% endif %}
    <li class="listing-item">
        <time datetime="{{ post.date | date:"%Y-%m-%d" }}">{{ post.date | date:"%Y-%m-%d" }}</time>
        <a href="{{ post.url }}" title="{{ post.title }}">{{ post.title }}</a>
    </li>
{% endfor %}
</ul>


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
        <br>
    {% endfor %}
</div>
{% endfor %}