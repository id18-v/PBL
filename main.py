from flask import Flask, render_template, request, redirect, url_for, session
import time

app = Flask(__name__)
app.secret_key = 'viteza_secreta_key'


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        action = request.form.get('action')
        distance = float(request.form.get('distance', 100))

        # Prima înregistrare a timpului
        if action == 'start':
            session['start_time'] = time.time()
            session['distance'] = distance
            return render_template('index.html',
                                   status='started',
                                   distance=distance)

        # A doua înregistrare a timpului și calculul vitezei
        elif action == 'stop':
            if 'start_time' in session:
                end_time = time.time()
                start_time = session['start_time']
                distance = session['distance']

                elapsed_time = end_time - start_time  # Timpul parcurs în secunde

                if elapsed_time > 0:
                    speed_mps = distance / elapsed_time  # Viteza în m/s
                    speed_kmph = speed_mps * 3.6  # Conversie în km/h (nu km/min cum era inițial)

                    # Salvăm rezultatele în sesiune
                    session['speed_mps'] = round(speed_mps, 2)
                    session['speed_kmph'] = round(speed_kmph, 2)
                    session['elapsed_time'] = round(elapsed_time, 2)

                    return redirect(url_for('results'))
                else:
                    return render_template('index.html', error="Eroare: timpul nu poate fi zero sau negativ.")
            else:
                return render_template('index.html', error="Trebuie să înregistrezi mai întâi timpul de start.")

    # Afișare inițială sau după resetare
    return render_template('index.html', status='init')


@app.route('/results')
def results():
    # Verificăm dacă avem rezultate în sesiune
    if 'speed_mps' in session:
        return render_template('results.html',
                               speed_mps=session['speed_mps'],
                               speed_kmph=session['speed_kmph'],
                               elapsed_time=session['elapsed_time'],
                               distance=session['distance'])
    else:
        return redirect(url_for('home'))


@app.route('/reset')
def reset():
    # Ștergem datele din sesiune
    session.pop('start_time', None)
    session.pop('speed_mps', None)
    session.pop('speed_kmph', None)
    session.pop('elapsed_time', None)
    session.pop('distance', None)
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)