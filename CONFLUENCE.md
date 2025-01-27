Title: Welcome to Atlassian Python API’s documentation! — Atlassian Python API 3.41.19 documentation

URL Source: https://atlassian-python-api.readthedocs.io/

Markdown Content:
You can adapt this file completely to your liking, but it should at least contain the root toctree directive.

Getting started[¶](https://atlassian-python-api.readthedocs.io/#getting-started "Link to this heading")
-------------------------------------------------------------------------------------------------------

Install package using pip:

`pip install atlassian-python-api`

Add a connection:

from atlassian import Confluence

confluence = Confluence(
    url='http://localhost:8090',
    username='admin',
    password='admin')

Or using Personal Access Token Note: this method is valid for Jira and Confluence (<7.9) Data center / server editions only! For Jira cloud, see below.

First, create your access token (check [https://confluence.atlassian.com/enterprise/using-personal-access-tokens-1026032365.html](https://confluence.atlassian.com/enterprise/using-personal-access-tokens-1026032365.html) for details) Then, just provide the token to the constructor:

confluence = Confluence(
    url='https://your-confluence-instance.company.com',
    token=confluence_access_token
)

To authenticate to the Atlassian Cloud Confluence

# Obtain an API token from: https://id.atlassian.com/manage-profile/security/api-tokens
# You cannot log-in with your regular password to these services.

confluence = Confluence(
    url='https://your-domain.atlassian.net',
    username=atlassian_username,
    password=atlassian_api_token,
    cloud=True)


*   [Confluence module](https://atlassian-python-api.readthedocs.io/confluence.html)
    *   [Get page info](https://atlassian-python-api.readthedocs.io/confluence.html#get-page-info)
    *   [Page actions](https://atlassian-python-api.readthedocs.io/confluence.html#page-actions)
    *   [Confluence Whiteboards](https://atlassian-python-api.readthedocs.io/confluence.html#confluence-whiteboards)
    *   [Template actions](https://atlassian-python-api.readthedocs.io/confluence.html#template-actions)
    *   [Get spaces info](https://atlassian-python-api.readthedocs.io/confluence.html#get-spaces-info)
    *   [Users and Groups](https://atlassian-python-api.readthedocs.io/confluence.html#users-and-groups)
    *   [CQL](https://atlassian-python-api.readthedocs.io/confluence.html#cql)
    *   [Other actions](https://atlassian-python-api.readthedocs.io/confluence.html#other-actions)

# Confluence module

Title: Confluence module — Atlassian Python API 3.41.19 documentation

URL Source: https://atlassian-python-api.readthedocs.io/confluence.html

Markdown Content:
Get page info[¶](https://atlassian-python-api.readthedocs.io/confluence.html#get-page-info "Link to this heading")
------------------------------------------------------------------------------------------------------------------

# Check page exists
# type of the page, 'page' or 'blogpost'. Defaults to 'page'
confluence.page_exists(space, title, type=None)

# Provide content by type (page, blog, comment)
confluence.get_page_child_by_type(page_id, type='page', start=None, limit=None, expand=None)

# Provide content id from search result by title and space
confluence.get_page_id(space, title)

# Provide space key from content id
confluence.get_page_space(page_id)

# Returns the list of labels on a piece of Content
confluence.get_page_by_title(space, title, start=None, limit=None)

# Get page by ID
# Example request URI(s):
#    http://example.com/confluence/rest/api/content/1234?expand=space,body.view,version,container
#    http://example.com/confluence/rest/api/content/1234?status=any
#    page_id: Content ID
#    status: (str) list of Content statuses to filter results on. Default value: [current]
#    version: (int)
#    expand: OPTIONAL: A comma separated list of properties to expand on the content.
#                   Default value: history,space,version
#                   We can also specify some extensions such as extensions.inlineProperties
#                   (for getting inline comment-specific properties) or extensions.resolution
#                   for the resolution status of each comment in the results
confluence.get_page_by_id(page_id, expand=None, status=None, version=None)

# The list of labels on a piece of Content
confluence.get_page_labels(page_id, prefix=None, start=None, limit=None)

# Get draft page by ID
confluence.get_draft_page_by_id(page_id, status='draft')

# Get all page by label
confluence.get_all_pages_by_label(label, start=0, limit=50, expand=None)

# Get all pages from Space
# content_type can be 'page' or 'blogpost'. Defaults to 'page'
# expand is a comma separated list of properties to expand on the content.
# max limit is 100. For more you have to loop over start values.
confluence.get_all_pages_from_space(space, start=0, limit=100, status=None, expand=None, content_type='page')

# Get list of pages from trash
confluence.get_all_pages_from_space_trash(space, start=0, limit=500, status='trashed', content_type='page')

# Get list of draft pages from space
# Use case is cleanup old drafts from Confluence
confluence.get_all_draft_pages_from_space(space, start=0, limit=500, status='draft')

# Search list of draft pages by space key
# Use case is cleanup old drafts from Confluence
confluence.get_all_draft_pages_from_space_through_cql(space, start=0, limit=500, status='draft')

# Info about all restrictions by operation
confluence.get_all_restrictions_for_content(content_id)

Page actions[¶](https://atlassian-python-api.readthedocs.io/confluence.html#page-actions "Link to this heading")
----------------------------------------------------------------------------------------------------------------

# Create page from scratch
confluence.create_page(space, title, body, parent_id=None, type='page', representation='storage', editor='v2', full_width=False)

# This method removes a page, if it has recursive flag, method removes including child pages
confluence.remove_page(page_id, status=None, recursive=False)

# Remove any content
confluence.remove_content(content_id):

# Remove page from trash
confluence.remove_page_from_trash(page_id)

# Remove page as draft
confluence.remove_page_as_draft(page_id)

# Update page if already exist
confluence.update_page(page_id, title, body, parent_id=None, type='page', representation='storage', minor_edit=False, full_width=False)

# Update page or create page if it is not exists
confluence.update_or_create(parent_id, title, body, representation='storage', full_width=False)

# Append body to page if already exist
confluence.append_page(page_id, title, append_body, parent_id=None, type='page', representation='storage', minor_edit=False)

# Set the page (content) property e.g. add hash parameters
confluence.set_page_property(page_id, data)

# Delete the page (content) property e.g. delete key of hash
confluence.delete_page_property(page_id, page_property)

# Move page
confluence.move_page(space_key, page_id, target_title, position="append")

# Get the page (content) property e.g. get key of hash
confluence.get_page_property(page_id, page_property_key)

# Get the page (content) properties
confluence.get_page_properties(page_id)

# Get page ancestors
confluence.get_page_ancestors(page_id)

# Attach (upload) a file to a page, if it exists it will update the
# automatically version the new file and keep the old one
# content_type is default to "application/binary"
confluence.attach_file(filename, name=None, content_type=None, page_id=None, title=None, space=None, comment=None)

# Attach (upload) a content to a page, if it exists it will update the
# automatically version the new file and keep the old one
# content_type is default to "application/binary"
confluence.attach_content(content, name=None, content_type=None, page_id=None, title=None, space=None, comment=None)

# Download attachments from a page to local system. If path is None, current working directory will be used.
confluence.download_attachments_from_page(page_id, path=None)

# Remove completely a file if version is None or delete version
confluence.delete_attachment(page_id, filename, version=None)

# Remove completely a file if version is None or delete version
confluence.delete_attachment_by_id(attachment_id, version)

# Keep last versions
confluence.remove_page_attachment_keep_version(page_id, filename, keep_last_versions)

# Get attachment history
confluence.get_attachment_history(attachment_id, limit=200, start=0)

# Get attachment for content
confluence.get_attachments_from_content(page_id, start=0, limit=50, expand=None, filename=None, media_type=None)

# Check has unknown attachment error on page
confluence.has_unknown_attachment_error(page_id)

# Export page as PDF
# api_version needs to be set to 'cloud' when exporting from Confluence Cloud
.
confluence.export_page(page_id)

# Set a label on the page
confluence.set_page_label(page_id, label)

# Delete Confluence page label
confluence.remove_page_label(page_id, label)

# Add comment into page
confluence.add_comment(page_id, text)

 # Fetch tables from Confluence page
confluence.get_tables_from_page(page_id)

# Get regex matches from Confluence page
confluence.scrap_regex_from_page(page_id, regex)

Confluence Whiteboards[¶](https://atlassian-python-api.readthedocs.io/confluence.html#confluence-whiteboards "Link to this heading")
------------------------------------------------------------------------------------------------------------------------------------

# Create  new whiteboard  - cloud only
confluence.create_whiteboard(spaceId, title=None, parentId=None)

# Delete existing whiteboard - cloud only
confluence.delete_whiteboard(whiteboard_id)

# Get whiteboard by id  - cloud only!
confluence.get_whiteboard(whiteboard_id)

Template actions[¶](https://atlassian-python-api.readthedocs.io/confluence.html#template-actions "Link to this heading")
------------------------------------------------------------------------------------------------------------------------

# Updating a content template
template_id = "<string\>"
name = "<string\>"
body = {"value": "<string\>", "representation": "view"}
template_type = "page"
description = "<string\>"
labels = [{"prefix": "<string\>", "name": "<string\>", "id": "<string\>", "label": "<string\>"}]
space = "<key_string\>"

confluence.create_or_update_template(name, body, template_type, template_id, description, labels, space)

# Creating a new content template
name = "<string\>"
body = {"value": "<string\>", "representation": "view"}
template_type = "page"
description = "<string\>"
labels = [{"prefix": "<string\>", "name": "<string\>", "id": "<string\>", "label": "<string\>"}]
space = "<key_string\>"

confluence.create_or_update_template(name, body, template_type, description=description, labels=labels, space=space)

# Get a template by its ID
confluence.get_content_template(template_id)

# Get all global content templates
confluence.get_content_templates()

# Get content templates in a space
confluence.get_content_templates(space)

# Get all global blueprint templates
confluence.get_blueprint_templates()

# Get all blueprint templates in a space
confluence.get_blueprint_templates(space)

# Removing a template
confluence.remove_template(template_id)

Get spaces info[¶](https://atlassian-python-api.readthedocs.io/confluence.html#get-spaces-info "Link to this heading")
----------------------------------------------------------------------------------------------------------------------

# Get all spaces with provided limit
# additional info, e.g. metadata, icon, description, homepage
confluence.get_all_spaces(start=0, limit=500, expand=None)

# Get information about a space through space key
confluence.get_space(space_key, expand='description.plain,homepage')

# Get space content (configuring by the expand property)
confluence.get_space_content(space_key, depth="all", start=0, limit=500, content_type=None, expand="body.storage")

# Get Space permissions set based on json-rpc call
confluence.get_space_permissions(space_key)

# Get Space export download url
confluence.get_space_export(space_key, export_type)

Users and Groups[¶](https://atlassian-python-api.readthedocs.io/confluence.html#users-and-groups "Link to this heading")
------------------------------------------------------------------------------------------------------------------------

# Get all groups from Confluence User management
confluence.get_all_groups(start=0, limit=1000)

# Get a paginated collection of users in the given group
confluence.get_group_members(group_name='confluence-users', start=0, limit=1000)

# Get information about a user through username
confluence.get_user_details_by_username(username, expand=None)

# Get information about a user through user key
confluence.get_user_details_by_userkey(userkey, expand=None)

# Change a user's password
confluence.change_user_password(username, password)

# Change calling user's password
confluence.change_my_password(oldpass, newpass)

CQL[¶](https://atlassian-python-api.readthedocs.io/confluence.html#cql "Link to this heading")
----------------------------------------------------------------------------------------------

# Get results from cql search result with all related fields
confluence.cql(cql, start=0, limit=None, expand=None, include_archived_spaces=None, excerpt=None)

Other actions[¶](https://atlassian-python-api.readthedocs.io/confluence.html#other-actions "Link to this heading")
------------------------------------------------------------------------------------------------------------------

# Clean all caches from cache management
confluence.clean_all_caches()

# Clean caches from cache management
# e.g.
# com.gliffy.cache.gon
# org.hibernate.cache.internal.StandardQueryCache_v5
confluence.clean_package_cache(cache_name='com.gliffy.cache.gon')

# Convert to Confluence XHTML format from wiki style
confluence.convert_wiki_to_storage(wiki)

# Get page history
confluence.history(page_id)

# Get content history by version number
confluence.get_content_history_by_version_number(content_id, version_number)

# Remove content history. It works as experimental method
confluence.remove_content_history(page_id, version_number)

# Compare content and check is already updated or not
confluence.is_page_content_is_already_updated(page_id, body)

# Add inline task setting checkbox method
confluence.set_inline_tasks_checkbox(page_id, task_id, status)

# Confluence Storage Format

```markdown
## Confluence Storage Format

Still need help? The Atlassian Community is here for you.

[Ask the community](https://community.atlassian.com)

This page describes the XHTML-based format that Confluence uses to store the content of pages, page templates, blueprints, blog posts and comments. This information is intended for advanced users who need to interpret and edit the underlying markup of a Confluence page.

We refer to the Confluence storage format as 'XHTML-based'. To be correct, we should call it XML, because the Confluence storage format does not comply with the XHTML definition. In particular, Confluence includes custom elements for macros and more. We're using the term 'XHTML-based' to indicate that there is a large proportion of HTML in the storage format.

You can view the Confluence storage format for a given page by choosing **More options > View Storage Format**. This option is only available if one of the following is true:

*   You are a Confluence administrator.
*   Your Confluence site has the Confluence Source Editor plugin installed and you have permission to use the source editor.

If you would like to edit the storage format for a page, your Confluence system administrator will need to install the Confluence Source Editor plugin.

**Clarification of terminology:** If you choose **More options > View Source**, you'll see the format used within the editor panel, not the storage format of the page.

### Headings

| Format type        | In Confluence 4.0 and later | What you will get |
|--------------------|-----------------------------|-------------------|
| Heading 1          | `<h1>Heading 1</h1>`         | <h1>Heading 1</h1> |
| Heading 2          | `<h2>Heading 2</h2>`         | <h2>Heading 2</h2> |
| Heading 3          | `<h3>Heading 3</h3>`         | <h3>Heading 3</h3> |
| Headings 4 to 6    | | are also available and follow the same pattern |

### Text effects

| Format type       | In Confluence 4.0 and later | What you will get                            |
|--------------------|-----------------------------|-------------------------------------------|
| strong/bold       | `<strong>strong text</strong>`     | **strong text**|
| emphasis          | `<em>Italics Text</em>`      | *Italics Text*                         |
| strikethrough     | `<span style="text-decoration: line-through;">strikethrough</span>` | <span style="text-decoration: line-through;">strikethrough</span> |
| underline         | `<u>underline</u>`            | <u>underline</u>|
| superscript       | `<sup>superscript</sup>`   | <sup>superscript</sup>                |
| subscript        | `<sub>subscript</sub>`       | <sub>subscript</sub>                |
| monospace          | `<code>monospaced</code>`      | `monospaced`                            |
| preformatted       | `<pre>preformatted text</pre>` | <pre>preformatted text</pre>               |
| block quotes      | `<blockquote><p>block quote</p></blockquote>`  | <blockquote><p>block quote</p></blockquote>|
| text color        | `<span style="color: rgb(255,0,0);">red text</span>`  | <span style="color: rgb(255,0,0);">red text</span> |
| small             | `<small>small text</small>` | <small>small text</small> |
| big               | `<big>big text</big>`        | <big>big text</big> |
| center-align      | `<p style="text-align: center;">centered text</p>` | <p style="text-align: center;">centered text</p>  |
| right-align       | `<p style="text-align: right;">right aligned text</p>` |  <p style="text-align: right;">right aligned text</p> |


### Text breaks

| Format type   | In Confluence 4.0 and later | What you will get                  |
|---------------|-----------------------------|-----------------------------------|
| New paragraph | `<p>Paragraph 1</p><p>Paragraph 2</p>` | Paragraph 1<br><br>Paragraph 2 |
| Line break    | `Line 1 <br /> Line 2`      | Note: Created in the editor using Shift + Return/Enter<br><br> Line 1<br>Line 2 |
| Horizontal rule | `<hr />` | — symbol |
| — symbol      | `&mdash;`                     | — |
| – symbol      | `&ndash;`                      | – |

### Lists

| Format type                   | In Confluence 4.0 and later                  | What you will get               |
|-------------------------------|----------------------------------------------|-------------------------------|
| Unordered list – round bullets | `<ul><li>round bullet list item</li></ul>`     | Round bullet list item        |
| Ordered list (numbered list)  | `<ol><li>numbered list item</li></ol>`      | Ordered list item      |
| Task Lists                   | `<ac:task-list><ac:task><ac:task-status>incomplete</ac:task-status><ac:task-body>task list item</ac:task-body></ac:task></ac:task-list>` | task list item |


### Links

| Format type                     | In Confluence 4.0 and later                                                                                                                      | What you will get                      |
|---------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------|
| Link to another Confluence page | `<ac:link><ri:page ri:content-title="Page Title" /><ac:plain-text-link-body><![CDATA[Link to another Confluence Page]]></ac:plain-text-link-body></ac:link>` | Link to another Confluence page       |
| Link to an attachment          | `<ac:link><ri:attachment ri:filename="atlassian_logo.gif" /><ac:plain-text-link-body><![CDATA[Link to a Confluence Attachment]]></ac:plain-text-link-body></ac:link>` | Link to an attachment                |
| Link to an external site       | `<a href="http://www.atlassian.com">Atlassian</a>`                                                                                               | Atlassian                            |
| Anchor link (same page)       | `<ac:link ac:anchor="anchor">  <ac:plain-text-link-body>    <![CDATA[Anchor Link]]>  </ac:plain-text-link-body></ac:link>`                         | Anchor Link                          |
| Anchor link (another page)    | `<ac:link ac:anchor="anchor">  <ri:page ri:content-title="pagetitle"/>  <ac:plain-text-link-body>    <![CDATA[Anchor Link]]>  </ac:plain-text-link-body></ac:link>` | Anchor Link                          |
| Link with an embedded image for the body | `<ac:link ac:anchor="Anchor Link"><ac:link-body><ac:image><ri:url ri:value="http://confluence.atlassian.com/images/logo/confluence_48_trans.png" /></ac:image></ac:link-body></ac:link>` | For rich content like images, you need to use ac:link-body to wrap the contents. |

**A note about link bodies**

All links received from the editor will be stored as plain text by default, unless they are detected to contain the limited set of mark up that we allow in link bodies. Here are some examples of markup we support in link bodies.

**An example of different link bodies**

```xml
<ac:link>
  <!-- Any resource identifier --> 
  <ri:page ri:content-title="Home" ri:space-key="SANDBOX" /> 
  <ac:link-body>Some <strong>Rich</strong> Text</ac:link-body>
</ac:link>
<ac:link>
  <ri:page ri:content-title="Plugin developer tutorial stuff" ri:space-key="TECHWRITING" />
  <ac:plain-text-link-body><![CDATA[A plain <text> link body]]></ac:plain-text-link-body>
</ac:link>
<ac:link>
  <ri:page ri:content-title="Plugin developer tutorial stuff" ri:space-key="TECHWRITING" />
  <!-- A link body isn't necessary. Auto-generated from the resource identifier for display. --> 
</ac:link>
```

The markup tags permitted within the `<ac:link-body>` are `<b>`, `<strong>`, `<em>`, `<i>`, `<code>`, `<tt>`, `<sub>`, `<sup>`, `<br>` and `<span>`.

### Images

| Format type    | In Confluence 4.0 and later                                                                                                                  |
|----------------|---------------------------------------------------------------------------------------------------------------------------------------------|
| Attached image | `<ac:image><ri:attachment ri:filename="atlassian_logo.gif" /></ac:image>`                                                                  |
| External image | `<ac:image><ri:url ri:value="http://confluence.atlassian.com/images/logo/confluence_48_trans.png" /></ac:image>`                             |

**Supported image attributes** (some of these attributes mirror the equivalent HTML 4 IMG element):

| Name        | Description                                           |
|-------------|-------------------------------------------------------|
| `ac:align`  | image alignment                                       |
| `ac:border` | Set to "true" to set a border                         |
| `ac:class`  | css class attribute.                                  |
| `ac:title`  | image tool tip.                                       |
| `ac:style`  | css style                                             |
| `ac:thumbnail`| Set to "true" to designate this image as a thumbnail.|
| `ac:alt`    | alt text                                              |
| `ac:height` | image height                                          |
| `ac:width`  | image width                                           |
| `ac:vspace` | the white space on the top and bottom of an image      |
| `ac:hspace` | the white space on the left and right of an image     |

### Tables

| Format type                                                                 | In Confluence 4.0 and later                                                                                                                                                                                                                                         | What you will get |
|-----------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------|
| Two column, two row (top header row)                                        | `<table><tbody><tr><th>Table Heading Cell 1</th><th>Table Heading Cell 2</th></tr><tr><td>Normal Cell 1</td><td>Normal Cell 2</td></tr></tbody></table>`                                                    | Table Heading Cell 1  Table Heading Cell 2<br>Normal Cell 1	Normal Cell 2 |
| Two column, three rows, 2nd and third with merged cells in first row |`<table><tbody><tr><th>Table Heading Cell 1</th><th>Table Heading Cell 2</th></tr><tr><td rowspan="2">Merged Cell</td><td>Normal Cell 1</td></tr><tr><td colspan="1">Normal Cell 2</td></tr></tbody></table>`| Table Heading Cell 1	Table Heading Cell 2<br>Merged Cell	Normal Cell 1<br>Normal Cell 2 |

### Page layouts

Confluence supports page layouts directly, as an alternative to macro-based layouts (using, for example, the section and column macros). This section documents the storage format XML created when these layouts are used in a page.

| Element name      | In Confluence 5.2 and later | Attributes                                                                                                                               |
|-------------------|-----------------------------|------------------------------------------------------------------------------------------------------------------------------------------|
| `ac:layout`       |                             | Indicates that the page has a layout. It should be the top level element in the page.                                                        |
| `ac:layout-section`|                             | Represents a row in the layout. It must be directly within the `ac:layout` tag. The type of the section indicates the appropriate number of cells and their relative widths. |
|                   |                             | `ac:type` |
| `ac:layout-cell`   |                             | Represents a column in a layout. It must be directly within the `ac:layout-section` tag. There should be an appropriate number of cells within the `layout-section` to match the `ac:type`. |

The recognized values of `ac:type` for `ac:layout-section` are:

| `ac:type`           | Expected number of cells | Description                                                          |
|--------------------|-------------------------|----------------------------------------------------------------------|
| `single`           | 1                       | One cell occupies the entire section.                               |
| `two_equal`        | 2                       | Two cells of equal width.                                            |
| `two_left_sidebar`  | 2                       | A narrow (~30%) cell followed by a wide cell.                         |
| `two_right_sidebar` | 2                       | A wide cell followed by a narrow (~30%) cell.                         |
| `three_equal`      | 3                       | Three cells of equal width.                                         |
| `three_with_sidebars`| 3                      | A narrow (~20%) cell at each end with a wide cell in the middle.     |

The following example shows one of the more complicated layouts from the old format built in the new. The word {content} indicates where further XHTML or Confluence storage format block content would be entered, such as `<p>` or `<table>` tags.

```xml
<ac:layout>
  <ac:layout-section ac:type="single">
     <ac:layout-cell>
        {content}
     </ac:layout-cell>
  </ac:layout-section>
 <ac:layout-section ac:type="three_with_sidebars">
     <ac:layout-cell>
       {content}
     </ac:layout-cell>
     <ac:layout-cell>
       {content}
     </ac:layout-cell>
     <ac:layout-cell>
       {content}
     </ac:layout-cell>
  </ac:layout-section>
  <ac:layout-section ac:type="single">
     <ac:layout-cell>
        {content}
     </ac:layout-cell>
  </ac:layout-section>
</ac:layout>
```

### Emojis

| Format type | In Confluence 4.0 and later | What you will get |
|-------------|-----------------------------|------------------|
| Emoticons   | `<ac:emoticon ac:name="smile" />`  | (smile)          |
|   | `<ac:emoticon ac:name="sad" />`    | (sad)            |
|   | `<ac:emoticon ac:name="cheeky" />` | (tongue)         |
|   | `<ac:emoticon ac:name="laugh" />`  | (big grin)       |
|   | `<ac:emoticon ac:name="wink" />`   | (wink)           |
|   | `<ac:emoticon ac:name="thumbs-up" />` | (thumbs up)   |
|   | `<ac:emoticon ac:name="thumbs-down" />`| (thumbs down)  |
|   | `<ac:emoticon ac:name="information" />`| (info)           |
|   | `<ac:emoticon ac:name="tick" />`   | (tick)          |
|   | `<ac:emoticon ac:name="cross" />`  | (error)          |
|   | `<ac:emoticon ac:name="warning" />` | (warning)        |

### Resource identifiers

Resource identifiers are used to describe "links" or "references" to resources in the storage format. Examples of resources include pages, blog posts, comments, shortcuts, images and so forth.

| Resource    | Resource identifier format                                                                                                                                   |
|-------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Page        | `<ri:page ri:space-key="FOO" ri:content-title="Test Page"/>` <br> Notes: <ul><li>`ri:space-key`: (optional) denotes the space key. This can be omitted to create a relative reference.</li><li>`ri:content-title`: (required) denotes the title of the page.</li></ul> |
| Blog Post    | `<ri:blog-post ri:space-key="FOO" ri:content-title="First Post" ri:posting-day="2012/01/30" />` <br> Notes: <ul><li>`ri:space-key`: (optional) denotes the space key. This can be omitted to create a relative reference.</li><li>`ri:content-title`: (required) denotes the title of the page.</li><li>`ri:posting-day`: (required) denotes the posting day. The format is YYYY/MM/DD.</li></ul>|
| Attachment  | `<ri:attachment ri:filename> ... resource identifier for the container of the attachment ...</ri:attachment>`<br>Notes:<ul><li>`ri:filename`: (required) denotes the name of the attachment.</li><li>the body of the `ri:attachment` element should be a resource identifier denoting the container of the attachment. This can be omitted to create a relative attachment reference (similar to `[foo.png]` in wiki markup).</li></ul>Examples:<ul><li>Relative Attachment Reference:  `<ri:attachment ri:filename="happy.gif" />`</li><li>Absolute Attachment Reference: `<ri:attachment ri:filename="happy.gif"><ri:page ri:space-key="TST" ri:content-title="Test Page"/></ri:attachment>`</li></ul>|
| URL         | `<ri:url ri:value="http://example.org/sample.gif"/>` <br> Notes: <ul><li>`ri:value`: (required) denotes the actual URL value.</li></ul>                                                                                                  |
| Shortcut    | `<ri:shortcut ri:key="jira" ri:parameter="ABC-123">` <br> Notes: <ul><li>`ri:key`: (required) represents the key of the Confluence shortcut.</li><li>`ri:parameter`: (required) represents the parameter to pass into the Confluence shortcut.</li></ul>  The example above is equivalent to `[ABC-123@jira]` in wiki markup.   |
| User        | `<ri:user ri:userkey="2c9680f7405147ee0140514c26120003"/>` <br> Notes: <ul><li>`ri:userkey`: (required) denotes the unique identifier of the user.</li></ul>                                                                     |
| Space       | `<ri:space ri:space-key="TST"/>` <br> Notes: <ul><li>`ri:space-key`: (required) denotes the key of the space.</li></ul>                                                                                                      |
| Content Entity | `<ri:content-entity ri:content-id="123"/>` <br> Notes: <ul><li>`ri:content-id`: (required) denotes the id of the content.</li></ul>                                                                                                 |

### Template variables

This screenshot shows a simple template:
*Screenshot of a template UI is not included here*

The template contains the following variables:

| Variable name | Type            | Values                     |
|---------------|-----------------|----------------------------|
| `$MyText`    | Single-line text|                            |
| `$MyMulti`   | Multi-line text | Size: 5 x 100              |
| `$MyList`    | List            | List items: Apples,Pears,Peaches |

The XML export produces the following code for the template:

```xml
<at:declarations>
  <at:string at:name="MyText" />
  <at:textarea at:columns="100" at:name="MyMulti" at:rows="5" />
  <at:list at:name="MyList">
    <at:option at:value="Apples" />
    <at:option at:value="Pears" />
    <at:option at:value="Peaches" />
  </at:list>
</at:declarations>

<p>This is Sarah's template</p>

<p>A single-line text variable:&nbsp;<at:var at:name="MyText" /></p>

<p>A multi-line text variable:&nbsp;<at:var at:name="MyMulti" /></p>

<p>A selection list:&nbsp;<at:var at:name="MyList" /></p>

<p>End of page.</p>
```

### Instructional Text

Instructional text allows you to include information on how to fill out a template for an end-user (the person using creating a page from the template). Instructional text will:

*   automatically clear all instructional text as the user types in a specific text block, and
*   automatically trigger a `@mention` prompt for user selection (for 'mention' type instructional text).

Screenshot: Example of instructional text.
*Screenshot of instructional text UI is not included here*

```xml
<ul>
    <li><ac:placeholder>This is an example of instruction text that will get replaced when a user selects the text and begins typing.</ac:placeholder></li>
</ul>
<ac:task-list>
    <ac:task>
        <ac:task-status>incomplete</ac:task-status>
        <ac:task-body><ac:placeholder ac:type="mention">@mention example. This placeholder will automatically search for a user to mention in the page when the user begins typing.</ac:placeholder></ac:task-body>
    </ac:task>
</ac:task-list>
```

# Confluence REST API examples:

```markdown
The REST API is based on open standards, allowing you to use any web development language to access it.

These examples use basic authentication with a username and password. You can also create a personal access token for authentication (Confluence 7.9 and later).

### Browse content

This example shows how you can browse content. If you're using Confluence 7.18 or later, there's a more performant option that might be useful below.

```bash
curl -u admin:admin http://localhost:8080/confluence/rest/api/content?limit=2 | python -mjson.tool
```

**Example result:**

```json
{
    "results": [
        {
            "id": "393219",
            "type": "page",
            "status": "current",
            "title": "First space",
            "extensions": {
                "position": 0
            },
            "_links": {
                "webui": "/display/FS/First+space",
                "edit": "/pages/resumedraft.action?draftId=393219",
                "tinyui": "/x/AwAG",
                "self": "http://localhost:8080/confluence/rest/api/content/393219"
            },
            "_expandable": {
                "container": "/rest/api/space/FS",
                "metadata": "",
                "operations": "",
                "children": "/rest/api/content/393219/child",
                "restrictions": "/rest/api/content/393219/restriction/byOperation",
                "history": "/rest/api/content/393219/history",
                "ancestors": "",
                "body": "",
                "version": "",
                "descendants": "/rest/api/content/393219/descendant",
                "space": "/rest/api/space/FS"
            }
        },
        {
            "id": "393229",
            "type": "page",
            "status": "current",
            "title": "Page 1",
            "extensions": {
                "position": 0
            },
            "_links": {
                "webui": "/display/FS/Page+1",
                "edit": "/pages/resumedraft.action?draftId=393229&draftShareId=f16d9e64-9373-4719-9df5-aec8102e5252",
                "tinyui": "/x/DQAG",
                "self": "http://localhost:8080/confluence/rest/api/content/393229"
            },
            "_expandable": {
                "container": "/rest/api/space/FS",
                "metadata": "",
                "operations": "",
                "children": "/rest/api/content/393229/child",
                "restrictions": "/rest/api/content/393229/restriction/byOperation",
                "history": "/rest/api/content/393229/history",
                "ancestors": "",
                "body": "",
                "version": "",
                "descendants": "/rest/api/content/393229/descendant",
                "space": "/rest/api/space/FS"
            }
        }
    ],
    "start": 0,
    "limit": 2,
    "size": 2,
    "_links": {
        "self": "http://localhost:8080/confluence/rest/api/content",
        "next": "/rest/api/content?limit=2&start=2",
        "base": "http://localhost:8080/confluence",
        "context": "/confluence"
    }
}
```

### Browse content (Confluence 7.18 and later)
This example shows how you can browse content in Confluence 7.18 and later. The scan endpoint provides better performance, but can only be used to browse pages (not blogs), and doesn't support offset, title, or creationdate parameters.

```bash
curl -u admin:admin http://localhost:8080/confluence/rest/api/content/scan?limit=2 | python -mjson.tool
```

**Example result:**

```json
{
    "results": [
        {
            "id": "393219",
            "type": "page",
            "status": "current",
            "title": "First space",
            "extensions": {
                "position": 0
            },
            "_links": {
                "webui": "/display/FS/First+space",
                "edit": "/pages/resumedraft.action?draftId=393219",
                "tinyui": "/x/AwAG",
                "self": "http://localhost:8080/confluence/rest/api/content/393219"
            },
            "_expandable": {
                "container": "/rest/api/space/FS",
                "metadata": "",
                "operations": "",
                "children": "/rest/api/content/393219/child",
                "restrictions": "/rest/api/content/393219/restriction/byOperation",
                "history": "/rest/api/content/393219/history",
                "ancestors": "",
                "body": "",
                "version": "",
                "descendants": "/rest/api/content/393219/descendant",
                "space": "/rest/api/space/FS"
            }
        },
        {
            "id": "393229",
            "type": "page",
            "status": "current",
            "title": "Page 1",
            "extensions": {
                "position": 0
            },
            "_links": {
                "webui": "/display/FS/Page+1",
                "edit": "/pages/resumedraft.action?draftId=393229&draftShareId=f16d9e64-9373-4719-9df5-aec8102e5252",
                "tinyui": "/x/DQAG",
                "self": "http://localhost:8080/confluence/rest/api/content/393229"
            },
            "_expandable": {
                "container": "/rest/api/space/FS",
                "metadata": "",
                "operations": "",
                "children": "/rest/api/content/393229/child",
                "restrictions": "/rest/api/content/393229/restriction/byOperation",
                "history": "/rest/api/content/393229/history",
                "ancestors": "",
                "body": "",
                "version": "",
                "descendants": "/rest/api/content/393229/descendant",
                "space": "/rest/api/space/FS"
            }
        }
    ],
    "cursor": "content:false:null",
    "nextCursor": "content:false:393229",
    "limit": 2,
    "size": 2,
    "_links": {
        "self": "http://localhost:8080/confluence/rest/api/content/scan",
        "next": "/rest/api/content/scan?cursor=content:false:393229&limit=2",
        "base": "http://localhost:8080/confluence",
        "context": "/confluence"
    }
}
```

### Browse content with pagination
To browse content with next or previous pagination use `_links.next` or `_links.prev`.

```bash
curl -u admin:admin http://localhost:8080/confluence/rest/api/content?limit=2&start=2 | python -mjson.tool
```

**Example result:**

```json
{
    "results": [
        {
            "id": "393239",
            "type": "page",
            "status": "current",
            "title": "Page 3",
            "extensions": {
                "position": 2
            },
            "_links": {
                "webui": "/display/FS/Page+3",
                "edit": "/pages/resumedraft.action?draftId=393239&draftShareId=9041c7ee-064e-448e-a354-d2117661ec0c",
                "tinyui": "/x/FwAG",
                "self": "http://localhost:8080/confluence/rest/api/content/393239"
            },
            "_expandable": {
                "container": "/rest/api/space/FS",
                "metadata": "",
                "operations": "",
                "children": "/rest/api/content/393239/child",
                "restrictions": "/rest/api/content/393239/restriction/byOperation",
                "history": "/rest/api/content/393239/history",
                "ancestors": "",
                "body": "",
                "version": "",
                "descendants": "/rest/api/content/393239/descendant",
                "space": "/rest/api/space/FS"
            }
        },
        {
            "id": "393244",
            "type": "page",
            "status": "current",
            "title": "Second space Home",
            "extensions": {
                "position": "none"
            },
            "_links": {
                "webui": "/display/SS/Second+space+Home",
                "edit": "/pages/resumedraft.action?draftId=393244",
                "tinyui": "/x/HAAG",
                "self": "http://localhost:8080/confluence/rest/api/content/393244"
            },
            "_expandable": {
                "container": "/rest/api/space/SS",
                "metadata": "",
                "operations": "",
                "children": "/rest/api/content/393244/child",
                "restrictions": "/rest/api/content/393244/restriction/byOperation",
                "history": "/rest/api/content/393244/history",
                "ancestors": "",
                "body": "",
                "version": "",
                "descendants": "/rest/api/content/393244/descendant",
                "space": "/rest/api/space/SS"
            }
        }
    ],
    "start": 2,
    "limit": 2,
    "size": 2,
    "_links": {
        "self": "http://localhost:8080/confluence/rest/api/content",
        "next": "/rest/api/content?limit=2&start=4",
        "prev": "/rest/api/content?limit=2&start=0",
        "base": "http://localhost:8080/confluence",
        "context": "/confluence"
    }
}
```

### Browse content with pagination (Confluence 7.18 and later)
This example shows how you can browse content with pagination in Confluence 7.18 and later. The scan endpoint provides better performance, but can only be used to browse pages (not blogs), and doesn't support offset, title, or creationdate parameters.

To browse content with next or previous pagination you can still use `_links.next` or `_links.prev`, or you can use the value of `nextCursor` and `prevCursor` to set the cursor in the next request.

To navigate forward using the value of `nextCursor` from the previous example:

```bash
curl -u admin:admin http://localhost:8080/confluence/rest/api/content/scan?cursor=content:false:393229&limit=2 | python -mjson.tool
```
**Example result:**
```json
{
    "results": [
        {
            "id": "393239",
            "type": "page",
            "status": "current",
            "title": "Page 3",
            "extensions": {
                "position": 2
            },
            "_links": {
                "webui": "/display/FS/Page+3",
                "edit": "/pages/resumedraft.action?draftId=393239&draftShareId=9041c7ee-064e-448e-a354-d2117661ec0c",
                "tinyui": "/x/FwAG",
                "self": "http://localhost:8080/confluence/rest/api/content/393239"
            },
            "_expandable": {
                "container": "/rest/api/space/FS",
                "metadata": "",
                "operations": "",
                "children": "/rest/api/content/393239/child",
                "restrictions": "/rest/api/content/393239/restriction/byOperation",
                "history": "/rest/api/content/393239/history",
                "ancestors": "",
                "body": "",
                "version": "",
                "descendants": "/rest/api/content/393239/descendant",
                "space": "/rest/api/space/FS"
            }
        },
        {
            "id": "393244",
            "type": "page",
            "status": "current",
            "title": "Second space Home",
            "extensions": {
                "position": "none"
            },
            "_links": {
                "webui": "/display/SS/Second+space+Home",
                "edit": "/pages/resumedraft.action?draftId=393244",
                "tinyui": "/x/HAAG",
                "self": "http://localhost:8080/confluence/rest/api/content/393244"
            },
            "_expandable": {
                "container": "/rest/api/space/SS",
                "metadata": "",
                "operations": "",
                "children": "/rest/api/content/393244/child",
                "restrictions": "/rest/api/content/393244/restriction/byOperation",
                "history": "/rest/api/content/393244/history",
                "ancestors": "",
                "body": "",
                "version": "",
                "descendants": "/rest/api/content/393244/descendant",
                "space": "/rest/api/space/SS"
            }
        }
    ],
    "cursor": "content:false:393229",
    "nextCursor": "content:false:393244",
    "prevCursor": "content:true:393239",
    "limit": 2,
    "size": 2,
    "_links": {
        "self": "http://localhost:8080/confluence/rest/api/content/scan?cursor=content:false:393229",
        "next": "/rest/api/content/scan?cursor=content:false:393244&limit=2",
        "prev": "/rest/api/content/scan?cursor=content:true:393239&limit=2",
        "base": "http://localhost:8080/confluence",
        "context": "/confluence"
    }
}
```
### Read content, and expand the body
This example shows how you can read content of a page with the body expanded.

```bash
curl -u admin:admin http://localhost:8080/confluence/rest/api/content/3965072?expand=body.storage | python -mjson.tool
```
**Example result:**
```json
{
    "_expandable": {
        "ancestors": "",
        "children": "",
        "container": "",
        "history": "/rest/api/content/3965072/history",
        "metadata": "",
        "space": "/rest/api/space/TST",
        "version": ""
    },
    "_links": {
        "base": "http://localhost:8080/confluence",
        "collection": "/rest/api/contents",
        "self": "http://localhost:8080/confluence/rest/api/content/3965072",
        "tinyui": "/x/kIA8",
        "webui": "/display/TST/Test+Page"
    },
    "body": {
        "editor": {
            "_expandable": {
                "content": "/rest/api/content/3965072"
            },
            "representation": "editor"
        },
        "export_view": {
            "_expandable": {
                "content": "/rest/api/content/3965072"
            },
            "representation": "export_view"
        },
        "storage": {
            "_expandable": {
                "content": "/rest/api/content/3965072"
            },
            "representation": "storage",
            "value": "<p>blah blah</p>"
        },
        "view": {
            "_expandable": {
                "content": "/rest/api/content/3965072"
            },
            "representation": "view"
        }
    },
    "id": "3965072",
    "title": "Test Page",
    "type": "page"
}
```

### Find pages or blogs

### Find pages by space key (Confluence 7.18 or later)
This example shows how you can find pages in Confluence 7.18 and later. The scan endpoint provides better performance, but can only be used to browse pages (not blogs), and doesn't support offset, title, or creationdate parameters.

This example shows how you can find a page by space key, with history expanded to find the creator.
```bash
curl -u admin:admin http://localhost:8080/confluence/rest/api/content/scan?spaceKey=FS&limit=2&expand=history | python -mjson.tool
```
**Example result:**
```json
{
    "results": [
        {
            "id": "393219",
            "type": "page",
            "status": "current",
            "title": "First space",
            "history": {
                "latest": true,
                "createdBy": {
                    "type": "anonymous",
                    "profilePicture": {
                        "path": "/confluence/s/-ze4av5/8804/0/_/images/icons/profilepics/anonymous.svg",
                        "width": 48,
                        "height": 48,
                        "isDefault": true
                    },
                    "displayName": "Anonymous"
                },
                "createdDate": "2022-04-27T07:15:13.012+10:00",
                "_links": {
                    "self": "http://localhost:8080/confluence/rest/api/content/393219/history"
                },
                "_expandable": {
                    "lastUpdated": "",
                    "previousVersion": "",
                    "contributors": "",
                    "nextVersion": ""
                }
            },
            "extensions": {
                "position": 0
            },
            "_links": {
                "webui": "/display/FS/First+space",
                "edit": "/pages/resumedraft.action?draftId=393219",
                "tinyui": "/x/AwAG",
                "self": "http://localhost:8080/confluence/rest/api/content/393219"
            },
            "_expandable": {
                "container": "/rest/api/space/FS",
                "metadata": "",
                "operations": "",
                "children": "/rest/api/content/393219/child",
                "restrictions": "/rest/api/content/393219/restriction/byOperation",
                "ancestors": "",
                "body": "",
                "version": "",
                "descendants": "/rest/api/content/393219/descendant",
                "space": "/rest/api/space/FS"
            }
        },
        {
            "id": "393229",
            "type": "page",
            "status": "current",
            "title": "Page 1",
            "history": {
                "latest": true,
                "createdBy": {
                    "type": "known",
                    "username": "admin",
                    "userKey": "2c9d802a8067b72f018067b876420000",
                    "profilePicture": {
                        "path": "/confluence/images/icons/profilepics/default.svg",
                        "width": 48,
                        "height": 48,
                        "isDefault": true
                    },
                    "displayName": "admin",
                    "_links": {
                        "self": "http://localhost:8080/confluence/rest/api/user?key=2c9d802a8067b72f018067b876420000"
                    },
                    "_expandable": {
                        "status": ""
                    }
                },
                "createdDate": "2022-04-27T07:15:18.097+10:00",
                "_links": {
                    "self": "http://localhost:8080/confluence/rest/api/content/393229/history"
                },
                "_expandable": {
                    "lastUpdated": "",
                    "previousVersion": "",
                    "contributors": "",
                    "nextVersion": ""
                }
            },
            "extensions": {
                "position": 0
            },
            "_links": {
                "webui": "/display/FS/Page+1",
                "edit": "/pages/resumedraft.action?draftId=393229&draftShareId=f16d9e64-9373-4719-9df5-aec8102e5252",
                "tinyui": "/x/DQAG",
                "self": "http://localhost:8080/confluence/rest/api/content/393229"
            },
            "_expandable": {
                "container": "/rest/api/space/FS",
                "metadata": "",
                "operations": "",
                "children": "/rest/api/content/393229/child",
                "restrictions": "/rest/api/content/393229/restriction/byOperation",
                "ancestors": "",
                "body": "",
                "version": "",
                "descendants": "/rest/api/content/393229/descendant",
                "space": "/rest/api/space/FS"
            }
        }
    ],
    "cursor": "content:false:null",
    "nextCursor": "content:false:393229",
    "limit": 2,
    "size": 2,
    "_links": {
        "self": "http://localhost:8080/confluence/rest/api/content/scan?spaceKey=FS&expand=history",
        "next": "/rest/api/content/scan?spaceKey=FS&cursor=content:false:393229&expand=history&limit=2",
        "base": "http://localhost:8080/confluence",
        "context": "/confluence"
    }
}
```
### Find a page by title and space key
This example shows how you can find a page by space key and title with history expanded to find the creator.
```bash
curl -u admin:admin -X GET "http://localhost:8080/confluence/rest/api/content?title=myPage%20Title&spaceKey=TST&expand=history" | python -mjson.tool
```
**Example result:**
```json
{
    "_links": {
        "self": "http://localhost:8080/confluence/rest/api/content"
    },
    "limit": 100,
    "results": [
        {
            "_expandable": {
                "ancestors": "",
                "body": "",
                "children": "/rest/api/content/950276/child",
                "container": "",
                "descendants": "/rest/api/content/950276/descendant",
                "metadata": "",
                "space": "/rest/api/space/TST",
                "version": ""
            },
            "_links": {
                "self": "http://localhost:8080/confluence/rest/api/content/950276",
                "tinyui": "/x/BIAO",
                "webui": "/display/TST/myPage+Title"
            },
            "history": {
                "_expandable": {
                    "lastUpdated": ""
                },
                "_links": {
                    "self": "http://localhost:8080/confluence/rest/api/content/950276/history"
                },
                "createdBy": {
                    "displayName": "A. D. Ministrator",
                    "profilePicture": {
                        "height": 48,
                        "isDefault": true,
                        "path": "/confluence/s/en_GB-1988229788/4960/NOCACHE1/_/images/icons/profilepics/default.png",
                        "width": 48
                    },
                    "type": "known",
                    "username": "admin"
                },
                "createdDate": "2014-03-07T17:08:20.326+1100",
                "latest": true
            },
            "id": "950276",
            "title": "myPage Title",
            "type": "page"
        }
    ],
    "size": 1,
    "start": 0
}
```

