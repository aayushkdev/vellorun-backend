#!/bin/bash

AUTH="Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzQ3ODI1MzE3LCJpYXQiOjE3NDc3Mzg5MTcsImp0aSI6IjQ3ZDY5ZTYzYTVlYTRlZjg5MWEwYmNkZGQyOWQ1ZWE4IiwidXNlcl9pZCI6MX0.0XN2fyJu_Co_Z3-G6we7F46okhbdlILU9Ax5_nD3ppI"
URL="https://vellorun-backend.vercel.app/api/places/"

post_place() {
  curl -s -X POST "$URL" \
    -H "$AUTH" \
    -H "Content-Type: application/json" \
    -d "$1"
}

post_place '{"name":"Mamu'\''s","type":"outside","description":"A Gali with weird peoples","coord_x":12.96627142,"coord_y":79.15652757,"level":2,"xp_reward":30,"category":"hangout"}'
