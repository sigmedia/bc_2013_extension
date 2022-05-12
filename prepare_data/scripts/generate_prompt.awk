function basename(file, a, n) {
    # Get basename with extension
    n = split(file, a, "/")
    tmp = a[n]

    n = split(tmp, a, ".")
    return a[1]
}

function join(array, start, end, sep, result, i)
{
    if (sep == "")
        sep = " "
    else if (sep == SUBSEP) # magic value
        sep = ""
    result = array[start]
    for (i = start + 1; i <= end; i++)
        result = result sep array[i]
    return result
}

BEGIN {
    i = 1
}

{
    array[i] = $3
    i = i+1
}

END {
    res = join(array, 1, i, " ")
    base = basename(FILENAME)
    print base "|" res
}
