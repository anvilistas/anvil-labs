Persistence
===========

Define simple classes for use in client side code and have those synchronised with
data tables rows.


Example
-------

Let's say we have an app that displays books. It has two tables, author and book, with
columns:

.. code-block::

   author
       name: text

   book
       title: text
       author: linked_column (to author table)


Using the persistence module, we can now define a class for book objects:


.. code-block:: python

   from anvil_labs.persistence import row_backed_class


   @row_backed_class
   class Book:
       pass


and we can use that class by creating an instance and telling it to fetch the associated
row from the database:


.. code-block:: python

   book = Book()
   book.get(title="Fluent Python")


our `book` object will automatically have each of the row's columns as an attribute:


.. code-block:: python

   assert book.title == "Fluent Python"


But what if we wanted our `book` object to include some information from the author table?
We can use a `LinkedAttribute` to fetch data from the linked row and include it as an
attribute on our object. Let's include the author's name as an attribute of a book:


.. code-block:: python

   from anvil_labs.persistence import row_backed_class, LinkedAttribute


   @row_backed_class
   class Book:
       author_name = LinkedAttribute(linked_column="author", linked_attr="name")


    book = Book()
    book.get(title="Fluent Python")

    assert book.author_name == "Luciano Ramalho" 



We can, of course, add whatever methods we want to our class. Let's add a property to
display the title and author of the book as a single string:


.. code-block:: python

   from anvil_labs.persistence import row_backed_class, LinkedAttribute


   @row_backed_class
   class Book:
       author_name = LinkedAttribute(linked_column="author", linked_attr="name")

       @property
       def display_text(self):
           return f"{self.title} by {self.author_name}"

   book = Book()
   book.get(title="Fluent Python")

   assert book.display_text == "Fluent Python by Luciano Ramalho"


Server Functions
----------------

**TODO**
