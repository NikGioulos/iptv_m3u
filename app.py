from flask import Flask, render_template, request, redirect, send_file, url_for
import services.iptv as iptv

app = Flask(__name__)


@app.route('/iptv', methods=['GET'])
def iptv_form():
    return render_template('iptv_form.html')


@app.route('/m3u', methods=['POST'])
def submit_iptv():
    server = request.form.get('iptvServer')
    username = request.form.get('iptvUsername')
    password = request.form.get('iptvPassword')
    keywords = request.form.get('iptvKeywords').split(",")
    result_as_file = "on" == str(request.form.get('iptvAsFile'))

    m3u_lines = iptv.fetch_m3u_lines(server, username, password, keywords)

    if result_as_file:
        filename = "_".join(keywords)
        write_file(f'generated/{filename}.m3u', m3u_lines)
        query_params = {'filename': filename}
        return redirect(url_for('m3u_file', **query_params))
    else:
        return render_template('m3u_content.html', m3u_lines=m3u_lines)


@app.route('/m3ufile', methods=['GET'])
def m3u_file():
    filename = request.args.get('filename')
    return send_file(f'generated/{filename}.m3u', as_attachment=True)


def write_file(filename, lines):
    with open(filename, 'w') as file:
        file.write("\n".join(lines))


if __name__ == '__main__':
    app.run(debug=False)
