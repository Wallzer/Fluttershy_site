import time

text1 = "a" * 2000
text2 = "a" * 2000






def lcs_dp(text1, text2):
    m, n = len(text1), len(text2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if text1[i - 1] == text2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    return dp[m][n]

def lcs_naive(i, j):
    if i == len(text1) or j == len(text2):
        return 0
    if text1[i] == text2[j]:
        return 1 + lcs_naive(i + 1, j + 1)
    else:
        return max(lcs_naive(i + 1, j), lcs_naive(i, j + 1))



# DP
start = time.time()
print("DP:", lcs_dp(text1, text2))
print("DP time:", round(time.time() - start, 4), "секунд")

