import discord
from discord.ext import commands
import asyncio
import schedule

client = discord.Client()
bot = commands.Bot(command_prefix="^")

SCHEDULES_FILENAME = "schedules.txt"


@bot.event
async def on_ready():
    bot.send_message(bot.get_channel('464866650290782219'), "asdasd")
    print("Bot is ready! :)")


@bot.command(name="schedulehere", pass_context=True, no_pm=True)
async def command_schedulehere(ctx: commands.Context):
    global channel
    channel = ctx.message.channel
    send_message(channel, "Schedules will be sent here.")


@bot.command(name="schedule", pass_context=True, no_pm=True)
async def command_schedule(ctx: commands.Context):
    try:
        if channel is not None:
            schedule_message(channel, *(str.split(ctx.message.content)[1::]))
            send_message(ctx.message.channel, "Message scheduled! :)")
        else:
            send_message(ctx.message.channel, str.format("Set a channel with {}schedulehere.", bot.command_prefix))
    except Exception as e:
        send_message(ctx.message.channel, bot.command_prefix + "schedule <message> <day> <time HH:MM>")
        print(str(e))


@bot.command(name="schedules", pass_context=True, no_pm=True)
async def command_schedules(ctx: commands.Context):
    try:
        schedules = get_schedules_from_file()
        send_message(ctx.message.channel, schedules if schedules is not None else "There are no schedules ;).")
    except Exception as e:
        send_message(ctx.message.channel, "Error.")
        print(str(e))


@bot.command(name="unschedule", pass_context=True, no_pm=True)
async def command_unschedule(ctx: commands.Context):
    try:
        remove_schedule_from_file(int(str.split(ctx.message.content)[1]))
        send_message(ctx.message.channel, "Unscheduled.")
    except Exception as e:
        send_message(ctx.message.channel, bot.command_prefix + "unschedule <index>")
        print(str(e))


def get_schedules_from_file():
    with open(SCHEDULES_FILENAME, 'r') as f:
        result = ""
        counter = 0

        for line in f.readlines():
            counter += 1
            params = str.split(line)
            print(params)
            result += str.format("{}. Say \"{}\" every {} at {}.\n", counter, params[0], str.capitalize(params[1]), params[2])

        return result if len(result) != 0 else None


def write_schedule_to_file(message: str, day: str, time: str):
    with open(SCHEDULES_FILENAME, 'a') as f:
        f.write(str.format("{} {} {}\n", message, day, time))


def remove_schedule_from_file(index: int):
    with open(SCHEDULES_FILENAME, 'r') as f:
        lines = f.readlines()

    del lines[index - 1]

    with open(SCHEDULES_FILENAME, 'w') as f:
        f.writelines(lines)


def send_message(channel: discord.Channel, message: str):
    loop = asyncio.get_event_loop()
    loop.create_task(bot.send_message(channel, message))


def schedule_message(channel: discord.Channel, message: str, day: str, time: str):
    day = str.lower(day)
    if day not in ("sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday"):
        raise Exception()

    getattr(schedule.every(), day).at(time).do(send_message, channel, message)
    write_schedule_to_file(message, day, time)


async def run_schedules():
    while 1:
        schedule.run_pending()
        await asyncio.sleep(1)


channel = None
bot.loop.create_task(run_schedules())
bot.run("NDUwMzE5NzY3NDI1OTA4NzM2.DiGEsA.K8QvYIzrns-E6L_FjhynHfOXiDA")

