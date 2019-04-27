---
layout: page
title: "Tags"
description: "Keywords"
header-img: "img/bkstone.jpg"  
---

## Tags List
<div id='tag_cloud' class="tags">
    {% for tag in site.tags %}
    <!-- <a href="#{{ tag[0] }}" title="{{ tag[0] }}" rel="{{ tag[1].size }}">{{ tag[0] }}</a> -->
    <a href="#{{ tag[0] }}" title="{{ tag[0] }}" rel="{{ tag[1].size }}">
        <span class="fa fa-tag listing-seperator" id="{{ tag[0] }}">
            <span class="tag-text">{{ tag[0]  &nbsp; }}</span>
        </span>
    </a>
    {% endfor %}
</div>

&nbsp;
## Whole List
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
    {% endfor %}
</div>
<br>
{% endfor %}


<script src="/media/js/jquery.tagcloud.js" type="text/javascript" charset="utf-8"></script> 
<script language="javascript">
$.fn.tagcloud.defaults = {
    size: {start: 1, end: 1, unit: 'em'},
      color: {start: '#f8e0e6', end: '#ff3333'}
};

$(function () {
    $('#tag_cloud a').tagcloud();
});
</script>