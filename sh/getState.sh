#!/bin/bash

curl "http://localhost:5050/api/getState?api-key=P9qgB1VWSHAsNUuYM9lcM8NxlHqB7GFa2ZxDb1---jI&actor=426a1c3b5afb4d9f9d3bd3cb3d3d9ea3" | grep -q '{"state": true}' && echo "True!"
