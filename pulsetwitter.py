import datetime
from flask import Flask
from flask_pymongo import PyMongo
import discord
import tweepy
from discord.ext import commands
import re

ckey = '7ctRJQdsF8YsmOkoLRstua9zE'  # Consumer Key
csecret = 'AyJq3LHXMTmPxfOozBWP2JaqjF13wCDR4ksTdPe2SgbFbjfRQ6'  # Consumer Secret
atoken = '894714120804552706-RmjiIj982hhmbX8koTk0cvgkHiwplyu'  # Access Token
asecret = 'wyBPSgkLPjVXpAcotS5sHbyKg6ILdtvjGKXb59TKhmvJQ'  # Access Secret

app = Flask(__name__)
app.config['MONGO_DBNAME'] = 'pulsenotify'
app.config['MONGO_URI'] = 'mongodb://mason:masonpulse1@ds055689.mlab.com:55689/pulsenotify'

mongo = PyMongo(app)

bot = commands.Bot(command_prefix='$')
bot.remove_command('pack')

tencodes = open('10codes.txt').read().splitlines()
twentyfivecodes = open('25codes.txt').read().splitlines()
fiftycodes = open('50codes.txt').read().splitlines()
hundredcodes = open('100codes.txt').read().splitlines()

twentyfivememberships = open('25memberships.txt').read().splitlines()
fiftymemberships = open('50memberships.txt').read().splitlines()


def ten_codes(quantity):
    # print(type(proxy))
    # print(proxy)
    total = ''
    aspen = []
    if quantity == 10:
        try:
            total = tencodes.pop(0)
            with open('10codes.txt', 'w') as f:
                for code in tencodes:
                    f.write(code + '\n')
            return total

        except IndexError:
            print('no more codes')

    elif quantity == 25:
        try:
            total = twentyfivecodes.pop(0)
            with open('25codes.txt', 'w') as f:
                for code in twentyfivecodes:
                    f.write(code + '\n')
            return total

        except IndexError:
            print('no more codes')
    elif quantity == 50:
        try:
            total = fiftycodes.pop(0)
            with open('50codes.txt', 'w') as f:
                for code in fiftycodes:
                    f.write(code + '\n')
                    return total

        except IndexError:
            print('no more codes')
    elif quantity == 100:
        try:
            total = hundredcodes.pop(0)
            with open('100codes.txt', 'w') as f:
                for code in hundredcodes:
                    f.write(code + '\n')
                    return total

        except IndexError:
            print('no more codes')


def discount_codes(quantity):
    if quantity == 50:
        try:
            total = twentyfivememberships.pop(0)
            with open('25memberships.txt', 'w') as f:
                for code in twentyfivememberships:
                    f.write(code + '\n')
            return total

        except IndexError:
            print('no more codes')

    elif quantity == 100:
        try:
            total = fiftymemberships.pop(0)
            with open('50memberships.txt', 'w') as f:
                for code in fiftymemberships:
                    f.write(code + '\n')
            return total

        except IndexError:
            print('no more codes')


@bot.event
async def on_ready():
    print('Logged in as ' + bot.user.name + ' (ID:' + bot.user.id + ') | Connected to ' + str(
        len(bot.servers)) + ' servers | Connected to ' + str(len(set(bot.get_all_members()))) + ' users')
    print('--------')
    print('Use this link to invite {}:'.format(bot.user.name))
    print('--------')


def check_tweets(tweetID):
    auth = tweepy.OAuthHandler(ckey, csecret)
    auth.set_access_token(atoken, asecret)
    api = tweepy.API(auth)

    tweet_id = tweetID

    try:
        tweet = api.get_status(tweet_id)
    except tweepy.error.TweepError:
        return

    if '@PulseNotify' in tweet.text:
        return True
    else:
        return False


@bot.command(pass_context=True)
async def verify(ctx, *args):
    if 'commands' in ctx.message.channel.name:
        global twitter
        author_id = ctx.message.author.id
        mesg = ' '.join(args)
        mesg = mesg.split(' ')
        twitter = mesg[0]
        user = mongo.db.twitterhandles
        status = user.find_one({'member_id': author_id})
        if '@' in str(twitter):
            embed = discord.Embed(title='You must verify without the @', color=0x15D0A0)
            await bot.send_message(ctx.message.channel, embed=embed)

        if status is None and '@' not in twitter:
            user.insert({'handle': twitter, 'member_id': author_id, 'points': 0, 'tweets': [], 'resetcounter': 0})
            embed = discord.Embed(title='Your twitter has been verified as {}'.format(twitter), color=0x15D0A0)
            await bot.send_message(ctx.message.channel, embed=embed)
        elif status is not None:
            embed = discord.Embed(title='You already have a verified twitter', color=0x15D0A0)
            mongo.db.twitterhandles.tweets.ensure_index("expireOn", expireAfterSeconds=5)
            await bot.send_message(ctx.message.channel, embed=embed)


@bot.command(pass_context=True)
async def pack(ctx, *args):
    pass


@bot.command(pass_context=True)
async def membership(ctx, *args):
    pass


@bot.command(pass_context=True)
async def resethandle(ctx, *args):
    if 'commands' in ctx.message.channel.name:
        author_id = ctx.message.author.id
        mesg = ' '.join(args)
        mesg = mesg.split(' ')
        twitter = mesg[0]
        user = mongo.db.twitterhandles
        status = user.find_one({'member_id': author_id})

        if status is None:
            embed = discord.Embed(title='There is no handle to change because you have not verified yet.',
                                  color=0x15D0A0)
            await bot.send_message(ctx.message.channel, embed=embed)

        elif status is not None:
            if status['resetcounter'] < 3:
                status['resetcounter'] += 1
                status['handle'] = twitter
                user.save(status)
                embed = discord.Embed(title='Your handle has been changed', color=0x15D0A0)
                await bot.send_message(ctx.message.channel, embed=embed)
                mongo.db.twitterhandles.tweets.ensure_index("expireOn", expireAfterSeconds=5)
            else:
                embed = discord.Embed(title='You have changed your handle too many times', color=0x15D0A0)
                await bot.send_message(ctx.message.channel, embed=embed)


@bot.command(pass_context=True)
async def points(ctx, *args):
    if 'commands' in ctx.message.channel.name:
        author_id = ctx.message.author.id
        user = mongo.db.twitterhandles
        status = user.find_one({'member_id': author_id})
        if status is not None:
            points = status['points']
            embed = discord.Embed(title=" ", color=0x15D0A0)
            embed.add_field(name='Points',
                            value="{}\n**You have {} pulse points**\n**Your handle is verified as {}**".format(
                                ctx.message.author.mention, status['points'], status['handle']))
            await bot.send_message(ctx.message.channel, embed=embed)


@bot.event
async def on_message(message):
    # do some extra stuff here

    if message.server is not None and 'commands' in message.channel.name:
        if message.content.startswith('$pack'):
            proxy_quantity = message.content.split(" ")[1]
            user = mongo.db.twitterhandles
            author_id = message.author.id
            status = user.find_one({'member_id': author_id})

            quantities = {'10': 25, '25': 50, '50': 100, '100': 200} #CHANGE PROXY COSTS HERE - (# OF POINTS IS THE VALUE WITHOUT QUOTES

            for key, value in quantities.items():
                if key == proxy_quantity:
                    final_quantity = value

                    if status is not None:
                        if status['points'] >= final_quantity:
                            status['points'] -= final_quantity
                            user.save(status)
                            embed = discord.Embed(title="CONGRATULATIONS", color=0x15D0A0)
                            embed.add_field(name='REDEEMED',
                                            value="You have redeemed a {} pack of proxies. You now have {} points. "
                                                  "Check your DM's for your proxy code.".format(proxy_quantity,
                                                                                                status['points']))
                            await bot.send_message(message.channel, embed=embed)

                            embed = discord.Embed(title="CONGRATULATIONS", color=0x15D0A0)
                            embed.add_field(name='PROXY CODE',
                                            value="{}\n\n You can redeem your proxies at https://pulseproxies.io/".format(
                                                ten_codes(final_quantity)))
                            # if message.channel.name is None:
                            await bot.send_message(message.author, embed=embed)
                            break
                        else:
                            embed = discord.Embed(title='Sorry...')
                            embed.add_field(name='NOT REDEEMED',
                                            value='You are too poor. You only have {} points'.format(status['points']))
                            await bot.send_message(message.channel, embed=embed)
                            return
                    # break
                    elif status is None:
                        embed = discord.Embed(title='You are not yet in the database.')
                        await bot.send_message(message.channel, embed=embed)
                        return
            else:
                embed = discord.Embed(title='That quantity is not available. Please use 10/25/50/100', color=0xe74c3c)
                embed.set_footer(text='@PulseNotify | @PulseProxies - @k0rnsyrup',
                                 icon_url='https://cdn.discordapp.com/attachments/487222109827891201/492206705472438284/5-02.png')
                await bot.send_message(message.channel, embed=embed)

    if message.server is not None and 'commands' in message.channel.name:
        if message.content.startswith('$membership'):
            membership_percentage = message.content.split(" ")[1]
            #membership_percentage = int(membership_percentage) * 2
            user = mongo.db.twitterhandles
            author_id = message.author.id
            status = user.find_one({'member_id': author_id})

            membership_quantities = {'25': 125, '50': 250} #CHANGE MEMBERSHIP COSTS HERE - (# OF POINTS IS THE VALUE WITHOUT QUOTES

            for key, value in membership_quantities.items():
                if key == membership_percentage:
                    final_quantity = value



                    if status is not None:
                        if status['points'] >= final_quantity:
                            status['points'] -= final_quantity
                            user.save(status)
                            embed = discord.Embed(title="CONGRATULATIONS", color=0x15D0A0)
                            embed.add_field(name='REDEEMED',
                                            value="You have redeemed a {}% off membership. You now have {} points. "
                                                  "Check your DM's for your discount code.".format(membership_percentage,
                                                                                                   status['points']))
                            await bot.send_message(message.channel, embed=embed)

                            embed = discord.Embed(title="CONGRATULATIONS", color=0x15D0A0)
                            embed.add_field(name='DISCOUNT CODE',
                                            value="{}\n\n You can redeem your proxies at https://pulseproxies.io/".format(
                                                discount_codes(final_quantity)))
                            # if message.channel.name is None:
                            await bot.send_message(message.author, embed=embed)
                            break
                        else:
                            embed = discord.Embed(title='Sorry...')
                            embed.add_field(name='NOT REDEEMED',
                                            value='You are too poor. You only have {} points'.format(status['points']))
                            await bot.send_message(message.channel, embed=embed)
                            return
                    # break
                    elif status is None:
                        embed = discord.Embed(title='You are not yet in the database.')
                        await bot.send_message(message.channel, embed=embed)
                        return
            else:
                embed = discord.Embed(title='That percentage is not available. Please use 25/50', color=0xe74c3c)
                embed.set_footer(text='@PulseNotify | @PulseProxies - @k0rnsyrup',
                                 icon_url='https://cdn.discordapp.com/attachments/487222109827891201/492206705472438284/5-02.png')
                await bot.send_message(message.channel, embed=embed)

    if message.server is not None and "commands" in message.channel.name:
        author_id = message.author.id
        user = mongo.db.twitterhandles
        status = user.find_one({'member_id': author_id})
        if status is not None:
            if status['handle'] in message.content and 'twitter.com' in message.content:
                tweet_link = message.content
                tweet_link = tweet_link.split('/')[5]
                # print(tweet_link)
                tweet_valid = check_tweets(tweet_link)
                # print(hello)
                if tweet_valid is True:
                    if tweet_link in status['tweets']:
                        embed = discord.Embed(title='You cannot use the same tweet twice.', color=0xe74c3c)
                        await bot.send_message(message.channel, embed=embed)
                    else:
                        status['tweets'].append(tweet_link)
                        status['points'] += 1
                        user.save(status)
                        embed = discord.Embed(title='You have been awarded one point', color=0x15D0A0)
                        await bot.send_message(message.channel, embed=embed)
                else:
                    embed = discord.Embed(title='You have not mentioned Pulse in your tweet.', color=0x15D0A0)
                    await bot.send_message(message.channel, embed=embed)

    await bot.process_commands(message)


@bot.command(pass_context=True)
async def store(ctx, *args):
    if 'commands' in ctx.message.channel.name:
        embed = discord.Embed(title='**WELCOME TO THE PULSE POINTS STORE**', color=0x15D0A0)
        embed.set_thumbnail(
            url='https://cdn.discordapp.com/attachments/499432680870641674/508162538962288641/pulseround.png')
        embed.add_field(name='**PROXIES**',
                        value='10 Pack - 25 Points\n25 Pack - 50 Points\n50 Pack - 100 Points\n100 Pack - 200 Points ')

        embed.add_field(name='**MEMBERSHIPS**',
                        value='25% OFF MEMBERSHIP - 125 points\n50% OFF MEMBERSHIP - 250 points', inline=False)
        embed.add_field(name='**COMMANDS TO REDEEM**',
                        value='`$pack <amount>`\n`$membership <amount>`')
        embed.set_footer(text='@PulseNotify | @PulseProxies - @k0rnsyrup',
                         icon_url='https://cdn.discordapp.com/attachments/487222109827891201/492206705472438284/5-02.png')
        await bot.send_message(ctx.message.channel, embed=embed)


@bot.command(pass_context=True)
async def award(ctx, *args):
    if 'commands' in ctx.message.channel.name and ctx.message.author.id == '203262972599074827':
        mesg = ' '.join(args)
        mesg = mesg.split(' ')
        selected_user = mesg[0]
        author_id = re.sub('[<@>]', '', selected_user)
        print(selected_user)
        num_points = mesg[1]
        user = mongo.db.twitterhandles
        status = user.find_one({'member_id': author_id})
        if status is not None:
            status['points'] += int(num_points)
            user.save(status)
            embed = discord.Embed(title=' ', color=0x15D0A0)
            embed.add_field(name='Awarded!', value='{} has been awarded {} points'.format(selected_user, num_points))
            await bot.send_message(ctx.message.channel, embed=embed)
        elif status is None:
            embed = discord.Embed(title=' ', color=0xe74c3c)
            embed.add_field(name='Error',
                            value='{} cannot be awarded because he is not in the database 🤔'.format(selected_user))
            await bot.send_message(ctx.message.channel, embed=embed)
    else:
        embed = discord.Embed(title='You cannot use this command.', color=0xe74c3c)
        await bot.send_message(ctx.message.channel, embed=embed)


if __name__ == '__main__':
    bot.run('NTA4MTY2MDM1NzE5ODQ3OTM4.Dr7SKg.sEokEpNzEP4eLqYVTMKpY4FWxU0')
