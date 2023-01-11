# HW3 - K-Means

## Method Explanation
1. Preprocess data
    - 參考 HW1 的 matrix multiplication，把 data, c1, c2 處理成 `(dim, (pid, value_dim)` ，方便之後依照 dimension 直接計算
    - 把 data 存成 `(pid, [v0, v1, ..., v57])` ，計算 centroid 用
2. Find centroid and closest_distance for each point (for loop 內）
    - 先用 `join` 把同個 dimension 的值都接在一起，再用 `map` 去計算 value 中 point 和 centroid 的 distance，最後 `reduceByKey` 把同一組 (point, centroid) 的 distance 相加，變成 `((pid, cid), distance)`
    - 為了後續比較各個 centroid 到底哪個最接近 point，用 `map` 把資料處理成 `(pid, (cid, distance))`
    - 接著用 `reduceByKey` 比較 distance，只回傳比較比較小的 distance 的 value，變成 `(pid, (cid, closest_distance))`
3. Match point and centroid (for loop 內）
    - 用 `map` 把 closest_distance 拿掉，變成 `(pid, cid)`
4. Recompute the centroid by points (for loop 內）
    - 先用 `join` 把 points_value 和前面得到的 (pid, cid) 合在一起，變成 `(pid, (cid, [v0, v1..., v57]))`
    - 用 `map` 把 pid 去掉，變成 `(cid, [v0, v1..., v57])` ，這些就是組成 centroid 的值
    - 利用 `reduceByKey` 把同個 centroid 的 value list 連在一起，再用 `map` 去將每個 dimension 的值相加再除以點數量，得到這輪新的 centroid 的值 `(cid, [v0, v1..., v57])`
    - 用跟 preprocess data 時一樣的方法把 centroid 變成 `(dim, (pid, value_dim)` 以利計算