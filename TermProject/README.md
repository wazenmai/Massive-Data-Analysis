# Term Project - Finding Similar Articles

題目說明：Given a set of BBCSports articles, Implement LSH using MapReduce to find out articles similarity.


## Preprocess
首先將所有文章讀取進來，並格外分出它們的 id 當作日後紀錄 document ID 使用。

`txtpreprocess` 利用 regular expression 去除標點符號和節選出單詞，並把所有單字變小寫避免重複計算 shingle。
## Shingling
這裏我們把文章單詞一個個拆解出來，以 3-shingle 的方式合在一起，由於我們實驗了兩種 min-hashing 的方式，`mapper_shingle_3` 會以 document ID 為 key，該 document 擁有的 shingle IDs 為 value 來表示 shingle-document boolean matrix，而 `new_mapper_shingle_3` 會以 shingle ID 為 key，擁有該 shingle 的 document IDs 為 value 來表示 boolean matrix。

1. `mapper_shingle_1` 將每篇文章處理後，把文章ID當成key，文章中每3個單字形成一個tuple，再將所有tuple收集起來當成value。
    - After `mapper_shingle_1`: `[(docId, [s1, s2, ..., ]), (docId, [s1, s2...,]), ...]` (s = shingle)

2. `mapper_shingle_2` 將上一個部分所有可能的shingle抓出當成key，擁有這個shingle的文章收集起來當成value。
    - After mapper_shingle_2: `[(s1, [doc1, doc2, ...]), (s2, [doc1, doc3...]), ...]` (s = shingle)
3. `mapper_shingle_3` 將上一個部分再轉變回以文章ID當成key，把所有shingle編號，並將每篇文章擁有的shingle ID收集起來當成value。
    - After mapper_shingle_3: `[(docID, [sID1, sID2...]), ...]` (sID = shingle ID)
    - After new_mapper_shingle_3: `[(sID1, [doc1, doc2, ...]), (sID2, [doc1, doc3...]), ...]` (s = shingle)

## Min-hashing
### Method 1 - Permuting rows

`build_minhash_func` 會產生 100 種 0 ~ `SHINGLES_SIZE` 的排列，當作 hash function 使用。

`mapper_minhash` 把 `doc_shingleID` 作為 input，再根據 `minhash_func` 去看該 document 有沒有那些 shingle，最後生成 `[(docID, [min-hashv1, min-hashv2, ..., min-hashv100])...]`。

After mapper_minhash: `[(docID, [min-hashv1, min-hashv2, ..., min-hashv100])...]`

### Method 2 - Row hashing
- p = MAGIC_NUMBER = 500009 (一個比 N 大的質數）
- N = SHINGLES_SIZE
- h(x) = ((ax + b) % p) % N    （參考講義 P.41 公式）

`create_hash_func` 創造出 100 種不同排列組合的參數 a, b，a 為 1 ~ 100，b 為 `randint(1, N)`。


`mapper_minhash_1` 以前面的 `shingleID_doc` 為 input，首先先算出 $h_i(r)$，再來 iterate 所有的 document 來創造 `((docID, hashIdx), h_r[hashIdx]`，到這邊就算出來所有可能的 M(i, c)，接著用 `reducer_minhash_1` 來拿取最小的 M(i, c)，接著用 `mapper_minhash_2` 和 `mapper_minhash_3` 來把 rdd 整理成方便 LSH 處理的 `[(docID, [min-hashv1, min-hashv2, ..., min-hashv100])...]`。

實作過程比較：method 2 比 method 1 速度快上非常多，同樣都是把 min_hash 完的值 collect 出來看，method 2 只需數秒，method 1 卻要長達好幾分鐘，可見優化是奏效的。

After mapper_minhash: `[(docID, [min-hashv1, min-hashv2, ..., min-hashv100])...]`

## Locality-sensitive-hashing
`LSH_band` 會把原本 100 個 min-hash value 兩個兩個 row 一組分成 50 個 band，再經過 `LSH_groupBand` 來整理成以 bandID 為 key，(docID, band-value) 為 value 的 rdd，到這裡就做完了 partition matrix into bands。

在 `LSH_pushBucket` 裡我們設計了一個 hash function: $(3000 b_1 + b_2) \% \text{SHINGLES_SIZE})$，$b_1, b_2$ 為 band 的第一個和第二個值，這樣每個 document 的 band 都被分配到一個 bucketID，就能把它整理成 `(bucketID, docID)`，再使用 `groupByKey().mapValues(list)` 就能把同一個 bucketID 的 documents 串在一起。

After LSH_band: `[(docID, [band1, band2..., band50])...]` (band = [min-hashv1, min-hashv2])

After LSH_groupBand: `[(bandID,  [(docID, band), (docID, band)])...]` each value of pair with len = 50

After LSH_putBucket: `[(bucketID, docID), (bucketID, docID)...]`

Then use groupByKey and mapValues: `[(bucketID, [docID, docID, ...]),...]`

`find_candidate` 如果遇到少於一個 documentID 的 bucket 就會回傳 (-1, -1)，其他狀況就會回傳裡面的 document 的兩個兩個排列組合為 key，value 為 1 的 key-value pair，並在外面把 (-1, -1) 用 `filter` 過濾掉，並用 `reduceByKey` 去算 candidate pair 被 match 到的數量再用 `sortBy` 讓它照多寡排序。

After find_candidate: `[((docID, docID), 1), ((docID, docID), 1)` (candidate_pair, pair_count)

## Output
用 jaccard 函數將兩個集合的 jaccard similarity 算出，並將將前10名 similarity 高的結果 print 出。
```
('052', '084') : 100.0 %
('012', '020') : 100.0 %
('047', '049') : 75.72 %
('030', '035') : 70.73 %
('049', '088') : 51.31 %
('023', '038') : 48.22 %
('048', '049') : 48.05 %
('014', '040') : 39.77 %
('047', '088') : 38.91 %
('047', '048') : 36.38 %
```