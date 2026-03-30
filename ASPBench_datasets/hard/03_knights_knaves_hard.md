# Problem Statement

The island has only two types of inhabitants: Knights (who always tell the truth) and Knaves (who always lie). Determine who is a knight and who is a knave among twenty-four inhabitants based on their statements.

## The Inhabitants

There are twenty-four inhabitants divided into three groups:

- **Group A**: Alice, Bob, Charlie, Diana, Ethan, Fiona, George, Hannah
- **Group B**: Ian, Julia, Kevin, Lily, Mason, Nina, Oliver, Paula
- **Group C**: Quentin, Rachel, Sam, Tina, Ursula, Victor, Wendy, Xavier

## The Statements

**Group A:**
- Alice says: "Hannah is a knave, and (Bob is a knave or Charlie is a knight), and **exactly** four of us in Group A are knights."
- Bob says: "Diana is the same type as me."
- Charlie says: "**Exactly** twelve of us are knights."
- Diana says: "Ethan and Fiona are of different types, and Hannah is a knave."
- Ethan says: "George is a knight if and **only** if Alice is a knight."
- Fiona says: "Bob and Charlie are of different types, and I am a knight."
- George says: "Alice and Hannah are of the same type."
- Hannah says: "**Exactly one** of Bob, Charlie, and Diana is a knight."

**Group B:**
- Ian says: "Alice and Paula are of the same type, and Julia is a knave."
- Julia says: "Kevin is a knight and Nina is a knight."
- Kevin says: "Either Oliver is a knight or Lily is a knave."
- Lily says: "**Exactly** four of us in Group B are knights, and Oliver is a knave."
- Mason says: "Bob and Ethan are of the same type, and Julia is a knave."
- Nina says: "Ian and Paula are of different types."
- Oliver says: "**Exactly** two of George, Hannah, Ian, and Julia are knights."
- Paula says: "Rachel is a knight if and **only** if Quentin is a knave."

**Group C:**
- Quentin says: "**At least** five of us in Group C are knights."
- Rachel says: "Charlie is a knight, Lily is a knight, and Victor is a knave."
- Sam says: "Tina is a knave, Oliver is a knave, and Ursula is a knave."
- Tina says: "Rachel is a knave or Mason is a knave."
- Ursula says: "Ian and Julia are both knights."
- Victor says: "**Exactly** two of Alice, Bob, Charlie, and Diana are knaves."
- Wendy says: "Victor is a knave, Ursula is a knave, and Xavier is a knight."
- Xavier says: "**Exactly** four of us in Group C are knights, and Sam is a knight."

## Constraints

1. **Knights** always tell the truth
2. **Knaves** always lie
3. Each person is **exactly** one type: knight or knave
4. Each statement is true if and **only** if the speaker is a knight
5. Each statement is false if and **only** if the speaker is a knave
6. The assignment **must** be logically consistent with **all** statements

## Objective

Find **any** valid solution that satisfies all constraints.

## Output Format

Your solution **must** output a JSON object with the following structure:

```json
{
  "alice": "knight" | "knave",
  "bob": "knight" | "knave",
  "charlie": "knight" | "knave",
  "diana": "knight" | "knave",
  "ethan": "knight" | "knave",
  "fiona": "knight" | "knave",
  "george": "knight" | "knave",
  "hannah": "knight" | "knave",
  "ian": "knight" | "knave",
  "julia": "knight" | "knave",
  "kevin": "knight" | "knave",
  "lily": "knight" | "knave",
  "mason": "knight" | "knave",
  "nina": "knight" | "knave",
  "oliver": "knight" | "knave",
  "paula": "knight" | "knave",
  "quentin": "knight" | "knave",
  "rachel": "knight" | "knave",
  "sam": "knight" | "knave",
  "tina": "knight" | "knave",
  "ursula": "knight" | "knave",
  "victor": "knight" | "knave",
  "wendy": "knight" | "knave",
  "xavier": "knight" | "knave"
}
```

Each person must be assigned either `"knight"` or `"knave"`.
