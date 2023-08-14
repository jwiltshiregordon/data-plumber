from main import plumber


@plumber(name="Integer from one to ten", color='rgb(153, 255, 163)')
def integer_one_to_ten(input_string):
    """Accepts integers in the range 1-10"""
    x = int(input_string)
    if 1 <= x <= 10:
        return x
    raise Exception("Integer is not in the range 1-10")


@plumber(
    name="Animal-Vegetable-Mineral",
    color='rgb(153, 255, 193)',
    specificity=30,
)
def animal_vegetable_or_mineral(input_string):
    """Accepts the strings "Animal", "Vegetable", and "Mineral" and nothing else"""
    if input_string in ["Animal", "Vegetable", "Mineral"]:
        return input_string
    raise Exception("Must be Animal, Vegetable, or Mineral")
