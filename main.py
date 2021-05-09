import os
import discord
from dotenv import load_dotenv
import asyncio
import datetime
from pytz import reference
from discord.ext import commands
from cal_setup import get_calendar_service
from zoneinfo import ZoneInfo
from convert import convert_to_RFC_datetime
import geocoder  # need to run pip install geocoder
from get_timezone import my_timezone

SCOPES = ["https://www.googleapis.com/auth/calendar"]

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD = os.getenv("DISCORD_GUILD")
# client = discord.Client()
client = commands.Bot(command_prefix="$")
client.remove_command("help")


@client.event
async def on_ready():
    for guild in client.guilds:
        if guild.name == GUILD:
            break

    print(
        f"{client.user} is connected to the following guild:\n"
        f"{guild.name}(id: {guild.id})"
    )


@client.group(invoke_without_command=True)
async def help(ctx):

    em = discord.Embed(colour=discord.Colour.blue(), title="Help")

    em.add_field(
        name="*create*",
        value="Description: Create an event using this command! \n **Syntax** $create <event_title> <start_date> <end_date> \n",
        inline=False,
    )
    em.add_field(
        name="*topfive*",
        value="Description: This command shows your next 5 events on your google calendar \n **Syntax** $topfive \n\n",
        inline=False,
    )
    em.add_field(
        name="*delete*",
        value="Description: This command deletes an event on your google calendar \n **Syntax** $delete <Event ID> \n\n",
        inline=False,
    )
    em.add_field(
        name="*update*",
        value="Description: This command updates an existing event on your google calendar \n **Syntax** $update <Event ID> <event_title> <start_date> <end_date> \n\n",
        inline=False,
    )

    await ctx.send(embed=em)


@client.command()
async def create(ctx, event_title, start_date, end_date):
    start_year = str(start_date).split("/", 1)[0]
    start_month = str(start_date).split("/", 2)[1]
    start_day = str(start_date).split("/", 3)[2]
    end_year = str(end_date).split("/", 1)[0]
    end_month = str(end_date).split("/", 2)[1]
    end_day = str(end_date).split("/", 3)[2]

    await ctx.channel.send("Description of the event:")

    try:
        desc = await client.wait_for("message", timeout=20.0)
    except asyncio.TimeoutError:
        return await ctx.channel.send("Sorry, you took too long. Try again!")

    if desc.content:

        await ctx.channel.send("Start Time: ")
        start_time = await client.wait_for("message")

        await ctx.channel.send("End Time: ")
        end_time = await client.wait_for("message")

        print(
            "TIME: "
            + convert_to_RFC_datetime(
                int(start_year),
                int(start_month),
                int(start_day),
                int(start_time.content),
                0,
            )
        )

        rightnow = datetime.datetime.now()
        localtime = reference.LocalTimezone()

        await ctx.channel.send(
            "Would you like to proceed with your current time zone: "
            + localtime.tzname(rightnow)
            + "?"
            + "\n reply with yes or no"
        )

        msg = await client.wait_for("message")

        if msg.content.lower() == "yes":

            service = get_calendar_service()
            event_result = (
                service.events()
                .insert(
                    calendarId="primary",
                    body={
                        "summary": event_title,
                        "description": desc.content,
                        "start": {
                            "dateTime": convert_to_RFC_datetime(
                                int(start_year),
                                int(start_month),
                                int(start_day),
                                int(start_time.content),
                                0,
                            ),
                            "timeZone": my_timezone(),
                        },
                        "end": {
                            "dateTime": convert_to_RFC_datetime(
                                int(end_year),
                                int(end_month),
                                int(end_day),
                                int(end_time.content),
                                0,
                            ),
                            "timeZone": my_timezone(),
                        },
                    },
                )
                .execute()
            )
            print("created event")
            print("id: ", event_result["id"])
            print(my_timezone())

            em = discord.Embed(colour=discord.Colour.red(), title="Event Summary")
            em.add_field(
                name=event_title,
                value="Title for the event: "
                + event_title
                + "\nDescription of the event: "
                + desc.content
                + "\nTime zone: "
                + localtime.tzname(rightnow)
                + "\nStart Date: "
                + start_date
                + "\nEnd Date: "
                + end_date
                + "\nStart time: "
                + start_time.content
                + ":00"
                + "\nEnd time: "
                + end_time.content
                + ":00"
                + "\nEvent Id: "
                + event_result["id"],
            )

            await ctx.send(embed=em)
        else:
            ctx.channel.send("You said no!")

        # print("summary: ", event_result["summary"])
    # print("starts at: ", event_result["start"]["dateTime"])
    # print("ends at: ", event_result["end"]["dateTime"])


@client.command()
async def topfive(ctx):
    service = get_calendar_service()

    # Call the Calendar API
    now = datetime.datetime.utcnow().isoformat() + "Z"  # 'Z' indicates UTC time
    print("Getting the upcoming 5 events")
    events_result = (
        service.events()
        # pylint: disable=maybe-no-member
        .list(
            calendarId="primary",
            timeMin=now,
            maxResults=5,
            singleEvents=True,
            orderBy="startTime",
        ).execute()
    )
    events = events_result.get("items", [])

    if not events:
        await ctx.channel.send("No upcoming events found.")
    for event in events:
        start = event["start"].get("dateTime", event["start"].get("date"))
        print(start, event["summary"])
        await ctx.send(start + event["summary"])


@client.command()
async def update(ctx, eventId, event_title, start_date, end_date):
    start_year = str(start_date).split("/", 1)[0]
    start_month = str(start_date).split("/", 2)[1]
    start_day = str(start_date).split("/", 3)[2]
    end_year = str(end_date).split("/", 1)[0]
    end_month = str(end_date).split("/", 2)[1]
    end_day = str(end_date).split("/", 3)[2]

    await ctx.channel.send("Description of the event:")

    try:
        desc = await client.wait_for("message", timeout=20.0)
    except asyncio.TimeoutError:
        return await ctx.channel.send("Sorry, you took too long. Try again!")

    if desc.content:

        await ctx.channel.send("Start Time: ")
        start_time = await client.wait_for("message")

        await ctx.channel.send("End Time: ")
        end_time = await client.wait_for("message")

        rightnow = datetime.datetime.now()
        localtime = reference.LocalTimezone()

        await ctx.channel.send(
            "Would you like to proceed with your current time zone: "
            + localtime.tzname(rightnow)
            + "?"
            + "\n reply with yes or no"
        )

        msg = await client.wait_for("message")

        if msg.content.lower() == "yes":

            service = get_calendar_service()
            event_result = (
                service.events()
                .update(
                    calendarId="primary",
                    eventId=eventId,
                    body={
                        "summary": event_title,
                        "description": desc.content,
                        "start": {
                            "dateTime": convert_to_RFC_datetime(
                                int(start_year),
                                int(start_month),
                                int(start_day),
                                int(start_time.content),
                            ),
                            "timeZone": my_timezone(),
                        },
                        "end": {
                            "dateTime": convert_to_RFC_datetime(
                                int(end_year),
                                int(end_month),
                                int(end_day),
                                int(end_time.content),
                            ),
                            "timeZone": my_timezone(),
                        },
                    },
                )
                .execute()
            )
            em = discord.Embed(colour=discord.Colour.red(), title="Event Summary")
            em.add_field(
                name=event_title,
                value="Title for the event: "
                + event_title
                + "\nDescription of the event: "
                + desc.content
                + "\nTime zone: "
                + localtime.tzname(rightnow)
                + "\nStart date: "
                + start_date
                + "\nEnd date: "
                + end_date
                + "\nStart time: "
                + start_time.content
                + ":00"
                + "\nEnd time: "
                + end_time.content
                + ":00"
                + "\n Event ID"
                + event_result["id"],
            )
            await ctx.send(embed=em)
        else:
            await ctx.channel.send("You said no!")


@client.command()
async def delete(ctx, eventId):
    service = get_calendar_service()
    try:
        service.events().delete(
            calendarId="primary",
            eventId=eventId,
        ).execute()
    except googleapiclient.errors.HttpError:
        await ctx.send("Failed to delete event")

    await ctx.send("Event deleted")


client.run(TOKEN)
