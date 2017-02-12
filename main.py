#!/usr/bin/env python

import webapp2
import cgi     # TODO:  remove if not used to escape stuff (vs. jinja2)
import jinja2
import os
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir))


class BlogPost(db.Model):
    title = db.StringProperty(required = True)
    blog_entry = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class Handler(webapp2.RequestHandler):
    """ A base RequestHandler class for our app.  """

    def renderError(self, error_code):
        """ Sends an HTTP error code + generic 'oops!' message to the client."""

        self.error(error_code)
        self.response.write("Oops! Something went wrong.")


class SlashHandler(Handler):
    def get(self):
        self.redirect('/blog')


class NewBlogPostHandler(Handler):
    def get(self):
        # t = jinja_env.get_template("
        self.response.write("get() for new blog post")

temp_blogs_data = { 
    'Blogs r Us': 'It was the best of times; it was the',
    'Second Blog Post': 'I hear the third time\'s the charm' }

class ViewBlogPostsHandler(Handler):
    def get(self):
        all_blogs = []
        for blog_item in temp_blogs_data:
            title = cgi.escape(blog_item)
            blog_entry = cgi.escape(temp_blogs_data[blog_item])
            b = BlogPost(title = title, blog_entry = blog_entry)
            all_blogs.append(b)
        t = jinja_env.get_template("bloghomepage.html")
        content = t.render(blog_posts = all_blogs)
        self.response.write(content)
        

        

app = webapp2.WSGIApplication([
    ('/', SlashHandler),
    ('/blog', ViewBlogPostsHandler),
    ('/blog/newpost', NewBlogPostHandler)
], debug=True)
