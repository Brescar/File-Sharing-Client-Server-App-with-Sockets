# Plan of action

## Authentication

Hold set of credentials in CSV/JSON/whatever kind of file as a workaround.
Users are not able to create an account, but only to log in.

## File sharing

Each user will have their own user resource directory, in which the file contents will be held.

## Notifications

Topic-based implementation for notification system on log in/log out of users and adding/modifying/removing files from user directory.


## Downloads

Client downloads the **whole** file to their own directory, including metadata and all.

# Responsabilities:

* Vali   - *
* Cristi - *
* Andrei - beautifying the code + refactoring + emulate Prettier 

# Code standards:

* 4-space indentation
* snake_case names for functions & variables, CamelCase for classes
* well divided code
* minimize use of if-else clauses in favour of only if w/ early returns (never nesting!!)
* use statically typed variables/parameters/functions w/ explicit return types if possible + docstrings