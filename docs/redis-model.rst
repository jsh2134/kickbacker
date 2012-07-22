Redis Model
#############

projects SET
backers SET


project
 - project:<id>
 -- name
 -- link
 -- img
 -- status
 -- title
 -- desc
 -- loc
 -- author
 -- pct-funded
 -- funded
 -- amount
 -- end

project:<id>:backers


backer
 - backer:<id>
 -- url
 -- name
 -- note
 -- img 



rs.hkeys()
rs.hget(key1, key2, key2val)

