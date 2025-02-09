| Variable                         | Output                                            | Example                            |
|----------------------------------|---------------------------------------------------|------------------------------------|
| **User Variables**               |                                                   |                                    |
| **{user}**                       | Displays the user's full tag (e.g., username#1234) | `JohnDoe#1234`                     |
| **{user.mention}**               | Mentions the user                                | `@JohnDoe`                         |
| **{user.id}**                    | Shows the user's ID                              | `123456789012345678`               |
| **{user.name}**                  | Shows the user's username                        | `JohnDoe`                          |
| **{user.avatar}**                | Displays the user's avatar URL                   | `https://cdn.discordapp.com/...`   |
| **{user.joined_at}**             | Shows when the user joined the server            | `3 days ago`                       |
| **{user.created_at}**            | Shows when the user's account was created        | `2 years ago`                      |
| **{user.discriminator}**         | Displays the user's discriminator (e.g., #1234)  | `1234`                             |
|                                  |                                                   |                                    |
| **Guild Variables**              |                                                   |                                    |
| **{guild.name}**                 | Shows the server’s name                          | `My Awesome Server`                |
| **{guild.icon}**                 | Displays the server’s icon URL                   | `https://cdn.discordapp.com/...`   |
| **{guild.id}**                   | Shows the server’s ID                            | `987654321098765432`               |
| **{guild.count}**                | Shows the server’s member count                  | `150`                              |
| **{guild.created_at}**           | Displays the server’s creation date              | `5 years ago`                      |
| **{guild.boost_count}**          | Shows the number of boosts in the server         | `12`                               |
| **{guild.booster_count}**        | Shows the number of boosters in the server       | `8`                                |
| **{guild.vanity}**               | Shows the server’s vanity URL code (or "none")   | `/awesome-vanity`                  |
| **{guild.boost_tier}**           | Shows the server’s boost level                   | `3`                                |
| **{guild.count.format}**         | Displays the member count in ordinal format      | `150th`                            |
| **{guild.boost_count.format}**   | Displays the boosts count in ordinal format      | `12th`                             |
| **{guild.booster_count.format}** | Displays the boosters count in ordinal format    | `8th`                              |
|                                  |                                                   |                                    |
| **Timestamp Variables**          |                                                   |                                    |
| **{date.now}**                   | Current date in PST                              | `January 5, 2025`                  |
| **{date.utc_timestamp}**         | Current date as a UNIX timestamp                | `1736077800`                       |
| **{date.now_proper}**            | Current date in a detailed format (PST)         | `Sunday, January 5, 2025`          |
| **{date.now_short}**             | Current date in MM/DD/YYYY format (PST)         | `01/05/2025`                       |
| **{date.now_shorter}**           | Current date in M/D/YY format (PST)             | `1/5/25`                           |
| **{time.now}**                   | Current time in 12-hour format (PST)            | `2:30 PM`                          |
| **{time.now_military}**          | Current time in 24-hour format (PST)            | `14:30`                            |
| **{date.utc_now}**               | Current date in UTC                              | `January 5, 2025`                  |
| **{date.utc_now_proper}**        | Current date in a detailed format (UTC)         | `Sunday, January 5, 2025`          |
| **{date.utc_now_short}**         | Current date in MM/DD/YYYY format (UTC)         | `01/05/2025`                       |
| **{date.utc_now_shorter}**       | Current date in M/D/YY format (UTC)             | `1/5/25`                           |
| **{time.utc_now}**               | Current time in 12-hour format (UTC)            | `10:30 PM`                         |
| **{time.utc_now_military}**      | Current time in 24-hour format (UTC)            | `22:30`                            |
