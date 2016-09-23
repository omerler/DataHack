from flask import Flask, request
from guess import manager
# from guess import manager
app = Flask(__name__)


@app.route("/search")
def search():
    print 'Connected!'
    answer = manager(request.args)
    if not answer:
        return 'bad syntax'
    return answer

@app.route("/")
def serve():
    return '''

<!DOCTYPE html>
<html lang="en">
    <head>
        <style>
            h2 {text-align:center;}
            p {text-align:center;}
            button {align-items:center}
        </style>
        <script>
            function myFunction() {
                var signature = document.getElementById('ourtext').value
    //            var signature = prompt("Please enter your method signature", "public static int example (double number)");
                if (signature != null) {
    //                document.getElementById("demo").innerHTML =  "process your signature: " + signature + "...";
                    $.ajax({
                        type: "GET",
                        url: "http://localhost:5000/search?query="+encodeURI(signature),
                        // data: { param: signature},
                        success: function(data){
                            console.log("success");
                        },
                        error: function(e) {
                            //called when there is an error
                            console.log("fail");
                        }
                    });
                }
            }
        </script>
        <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.8.3/jquery.min.js"></script>
    </head>
    <body text="white">
        <br>
        <p>Enter Method signature</p>
        <form align="middle">
            <input type="text" id="ourtext" name="insertSignature" width="1000"><br>
            <br><br><br><br><br><br>
            <img  src="magic.jpg"  onclick="myFunction()" width="150" height="150" style="cursor: pointer">
        </form>
        <p><b>Click on the hat to see our magic...</b></p>
        <p id="demo"></p>
        <p id="answer"></p>
        <br><br><br><br><br><br>
        <p id="provided">Provided to you by SourceHack team.</p>
        <script>
            document.body.style.backgroundColor = "black";
        </script>
    </body>
</html>
'''

if __name__ == "__main__":
    print 'yo'
    app.run()
