import discord
from discord.ext import commands
import asyncio
import schedule
import re

client = discord.Client()
bot = commands.Bot(command_prefix="^")

SCHEDULES_FILENAME = "schedules.txt"
TOKEN = "NDUwMzE5NzY3NDI1OTA4NzM2.DiGEsA.K8QvYIzrns-E6L_FjhynHfOXiDA"
MESSAGE_CHARACTER_LIMIT = 2000


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
            schedule_str = ctx.message.content.replace(bot.command_prefix + "schedule ", "")
            schedule_message(channel, *split_schedule(schedule_str))         
            write_schedule_to_file(schedule_str)                             
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
        schedules_str = ""
        if len(schedules) == 0:
            send_message(ctx.message.channel, "There are no schedules ;).")
            return
            
        for m in split_schedules_into_messages(schedules):
            send_message(ctx.message.channel, m)
    except Exception as e:
        send_message(ctx.message.channel, "Error.")
        print(str(e))


@bot.command(name="unschedule", pass_context=True, no_pm=True)
async def command_unschedule(ctx: commands.Context):
    try:
        remove_schedule_from_file(int(ctx.message.content.split()[1]))
        send_message(ctx.message.channel, "Unscheduled.")
    except Exception as e:
        send_message(ctx.message.channel, bot.command_prefix + "unschedule <index>")
        print(str(e))
        
        
def split_schedule(schedule: str) -> list:
    if '"' not in schedule:
        return schedule.split()
    
    message = schedule[schedule.find('"') + 1 : schedule.rfind('"'):]
    day, time = schedule[schedule.rfind('"') + 2 ::].split()
    return [message, day, time]
    
    
def find_mentions(s: str) -> list:
    mentions = list()
    possibilites = ['@everyone', '@here']
    for p in possibilites:
        if p in s:
            mentions.append(p)
    
    return mentions
    
    
def split_schedules_into_messages(schedules: list) -> list:
    messages = [""]
    for schedule in schedules:
        if len(messages[len(messages)-1]) + len(schedule) >= MESSAGE_CHARACTER_LIMIT:
            messages.append(schedule)
        else:
            messages[len(messages) - 1] += schedule
                
    return messages


def get_schedules_from_file() -> list:
    with open(SCHEDULES_FILENAME, 'r') as f:
        schedules = list()
        counter = 0

        for line in f.readlines():
            counter += 1
            schedule_list = split_schedule(line)
            for m in find_mentions(schedule_list[0]):
                schedule_list[0] = schedule_list[0].replace(m, "`" + m + "`")
            
            schedules.append(str.format("{}. Say \"{}\" every {} at {}.\n", counter, schedule_list[0], str.capitalize(schedule_list[1]), schedule_list[2]))

        return schedules


def write_schedule_to_file(schedule: str):
    with open(SCHEDULES_FILENAME, 'a') as f:
        if schedule[-1] != '\n':
            schedule += '\n'
        f.write(schedule)


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


async def run_schedules():
    while 1:
        schedule.run_pending()
        await asyncio.sleep(1)


channel = None
bot.loop.create_task(run_schedules())
bot.run(TOKEN)

