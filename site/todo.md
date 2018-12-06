# Things that must be fixed before launch
* Session tokens must have their IP address validated
* Rate limiting needs to be added to crucial forms (maybe even all endpoints)
* Automatic black listing needs to be added based on rules (such as number of invalid requests in x timeframe)
* Somewhat more clean code

# Things that would be nice to have before launch
* A 404 Page: Page not found
* A 401 Page: Not authorized (For user routes requiring authentication and are not authenticated)
* A 403 Page: Forbidden (For admin and superuser routes)
* A 500 Page: Internal Server Error (For whenever there's an error not otherwise handled)
* A 400 Page: Bad request (For errors such as submitting an incomplete form via ajax)
