---
layout: page
title: "Archive"
description: "藏书楼"
header-img: "img/stars.jpg"
---



{% for post in site.posts %}
    {% capture y %}{{post.date | date:"%Y"}}{% endcapture %}
    {% if year != y %}
        {% assign year = y %}
        <!-- <li class="listing-seperator">{{ y }}</li> -->
        <h3>{{ y }}</h3>
    {% endif %}
    <ul class="listing">
        <li class="listing-item">
            <time datetime="{{ post.date | date:"%Y-%m-%d" }}">{{ post.date | date:"%Y-%m-%d" }}</time>
            <a href="{{ post.url }}" title="{{ post.title }}">{{ post.title }}</a>
        </li>
    </ul>
{% endfor %}


