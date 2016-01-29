import re

import feedparser

from django import template
from django.conf import settings
from django.utils.safestring import mark_safe

register = template.Library()

@register.tag(name='wordpress_rss')
def do_rss_latest(parser, token):
    """
    A template tag to grab the latest articles from a given feed.
    The first argument is the category.
    The second argument is the number of items to retrieve.
    The third argument (after 'as') is the variable to store the result in.
    """

    try:
        tag_name, args = token.contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError(
            "%r tag requires three arguments:"
            + "category, number of items to retrieve and a variable name"
            % token.contents.split()[0]
        )
    m = re.search(r'(.*?) ([0-9]+) as (\w+)', args)

    if not m:
        raise template.TemplateSyntaxError(
            "%r has invalid arguments" % tag_name
        )

    category, num_items, var_name = m.groups()
    print("should be trying: %s %s %s" % (category, num_items, var_name))

    try:
        number_of_items = int(num_items)
    except ValueError:
        raise template.TemplateSyntaxError(
            "%r's second argument must be a number" % tag_name
        )

    print("about to GetRSSLategest")
    return GetRSSLatest(category, number_of_items, var_name)


class GetRSSLatest(template.Node):
    def __init__(self, category, number_of_items, var_name):
        self.category = template.Variable(category)
        self.number_of_items = number_of_items
        self.var_name = var_name
        print("after init: %s %s %s" % (self.category, self.number_of_items, self.var_name))

    def render(self, context):
        print("RENDERING!")
        try:
            print("self.category: " + str(self.category))
            actual_category = self.category.resolve(context)
            print("actual_cateogy: " + str(actual_category))
        except template.VariableDoesNotExist:
            return ''
        context[self.var_name] = []
        feed_url = getattr(
            settings,
            'WORDPRESS_RSS_BASE_URL', 
            'http://news.opensciencedatacloud.org'
#	    'http://opencloudconsortium.org'
        )
        print("feed_url: %s" % feed_url)

        if actual_category is not None:
            feed_url += '/category/'
            feed_url += str(actual_category)

        feed_url += '/feed/'
        
        print("feed_url: %s" % feed_url)
        d = feedparser.parse(feed_url)
        for item in d.entries[:self.number_of_items]:
            try:
                publish_datetime = item.published_parsed

                rss_item = {
                    'title': item.title_detail['value'],
                    'href': item.link,
                    'content': mark_safe(item.content[0]['value']),
                    'published': "%s/%s/%s" % (publish_datetime[0], publish_datetime[1], publish_datetime[2]),
                    'author': item.author
                }
                context[self.var_name].append(rss_item)
            except AttributeError:
                pass
        return ''

