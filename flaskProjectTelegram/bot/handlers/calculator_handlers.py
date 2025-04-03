from telegram import Update
from telegram.ext import ContextTypes
async def calc_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler for the /calc command that performs basic calculations
    Usage: /calc 2 + 2
    """
    try:
        # Join all arguments after the command
        expression = " ".join(context.args)
        if not expression:
            await update.message.reply_text(
                "Please provide an expression to calculate.\nExample: calc 2 + 2"
            )
            return
        # Evaluate the expression safely
        allowed_chars = set("0123456789+-/*() ")
        if not all(c in allowed_chars for c in expression):
            await update.message.reply_text(
                "Invalid characters in expression. Only numbers and basic operators (+, -, *, /) are allowed."
            )
            return
        result = eval(expression)
        await update.message.reply_text(f"{expression} = {result}")

    except (SyntaxError, ZeroDivisionError, NameError) as e:
        await update.message.reply_text(
            f"Error in calculation: {str(e)}\nPlease check your expression."
        )