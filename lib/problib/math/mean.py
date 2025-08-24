def arithmetic_mean(numbers: list[int | float]) -> float:
    """Calculate the arithmetic mean of a list of numbers. Returns zero if the list is empty.

    Args:
        numbers (list[int  |  float]): list of numbers to calculate the mean for

    Returns:
        float: arithmetic mean of the numbers

    Raises:
        ValueError: if the list of numbers is empty
    """
    if not numbers:
        raise ValueError("The list of numbers cannot be empty.")
    return sum(numbers) / len(numbers)


def geometric_mean(numbers: list[int | float], shift: int = 10) -> float:
    """Calculate the geometric mean of a list of numbers, with an optional shift value.

    Args:
        numbers (list[int  |  float]): list of numbers to calculate the mean for
        shift (int, optional): The shift value to be added to each number before calculating the geometric mean. Defaults to 10.

    Raises:
        ValueError: if the list of numbers is empty

    Returns:
        float: geometric mean of the numbers after applying the shift
    """
    if not numbers:
        raise ValueError("The list of numbers cannot be empty.")

    product = 1
    for number in numbers:
        product *= number + shift
    product = product - shift

    return product ** (1 / len(numbers))


if __name__ == "__main__":
    # Test cases for the functions
    amean = arithmetic_mean([0.05, 50.0])
    assert amean == 25.025

    gmean = geometric_mean([0.05, 50.0])
    assert gmean == 24.351591323771842

    print("All tests passed!")
