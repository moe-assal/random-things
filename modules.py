from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from white_party import db, app
from flask import url_for
from datetime import datetime, timedelta

comment_likes_table = db.Table('comment_likes_table',
                               db.Column('comment_id', db.Integer, db.ForeignKey('comment.id')),
                               db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
                               )


proposals_up_voting_table = db.Table('proposals_up_voting_table',
                                     db.Column('proposal_id', db.Integer, db.ForeignKey('proposal.id')),
                                     db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
                                     )


follow_ship_table = db.Table('follow_ship_table',
                             db.Column('follower_id', db.Integer, db.ForeignKey('users.id')),
                             db.Column('followed_id', db.Integer, db.ForeignKey('users.id'))
                             )


class Users(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    membership_id = db.Column(db.String(20), nullable=False)
    description = db.Column(db.String(500), nullable=False, default='user likes to stay anonymous')
    user_name = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(20), nullable=False)
    gender = db.Column(db.Integer, nullable=False)
    profile_img = db.Column(db.String(40))
    email = db.Column(db.String(80), nullable=False)
    date_joined = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    laws_ = db.relationship('Law', backref='author')
    proposals = db.relationship('Proposal', backref='author')
    comments = db.relationship('Comment', backref='author')

    followed = db.relationship(
        'Users', secondary=follow_ship_table,
        primaryjoin=(follow_ship_table.c.follower_id == id),
        secondaryjoin=(follow_ship_table.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

    proposals_voted_for = db.relationship('Proposal', secondary=proposals_up_voting_table,
                                          backref=db.backref('voters', lazy='dynamic'))
    comments_liked = db.relationship('Comment', secondary=comment_likes_table,
                                     backref=db.backref('users_likes', lazy='dynamic'))
    laws_voted_in = db.relationship('VotePaper')

    def __init__(self, membership_id, name, password, email, gender):
        self.user_name = name
        self.gender = 1 if gender == 'male' else 0
        self.password = password
        self.membership_id = membership_id
        self.email = email
        self.profile_img = gender + '.jpg'

    def __repr__(self):
        return 'user ' + self.user_name

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        found_user = self.followed.filter_by(id=user.id).all()
        return True if found_user else False

    def profile_image_url(self):
        return url_for('static', filename='profile-image/' + self.profile_img)

    def get_gender(self):
        return 'male' if self.gender == 1 else 'female'

    def get_reset_token(self, expire_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expire_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return Users.query.get(user_id)

    def __meta_data__(self, endpoint):
        if endpoint in ['users.user_profile', 'users.profile']:
            data = [
                {
                    'name': 'title',
                    'content': 'user profile - ' + self.user_name
                },
                {
                    'name': 'description',
                    'content': 'About - ' + self.description[:155] + '...'
                }
            ]
            return data
        return None


class Law(db.Model):
    __tablename__ = 'law'
    __bind_key__ = 'laws'
    __searchable__ = ['id', 'title', 'info']

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable=False, default='title')
    info = db.Column(db.Text, nullable=False)
    explanation = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    edit_proposals = db.relationship('Proposal', backref='posted_at')

    vote_papers = db.relationship('VotePaper')
    up_votes = db.Column(db.Integer, nullable=False, default=0)
    down_votes = db.Column(db.Integer, nullable=False, default=0)

    title_arabic = db.Column(db.Text, nullable=True)
    info_arabic = db.Column(db.Text, nullable=True)
    explanation_arabic = db.Column(db.Text, nullable=True)

    def __init__(self, title, info, explanation, author):
        self.title = title
        self.info = info
        self.explanation = explanation
        self.author = author

    def __repr__(self):
        return 'law ' + str(self.id)

    def __meta_data__(self, endpoint):
        if endpoint == 'laws.law':
            data = [
                {
                    'name': 'title',
                    'content': 'law - ' + self.title
                },
                {
                    'name': 'description',
                    'content': self.info[:155] + '...'
                }
            ]
            return data
        return None


class Proposal(db.Model):
    __tablename__ = 'proposal'
    __bind_key__ = 'proposals'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False, default='title')
    info = db.Column(db.Text, nullable=False)
    explanation = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    up_votes = db.Column(db.Integer, nullable=False, default=0)

    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    law_id = db.Column(db.Integer, db.ForeignKey('law.id'))
    comments = db.relationship('Comment', backref='posted_at')

    title_arabic = db.Column(db.Text, nullable=True)
    info_arabic = db.Column(db.Text, nullable=True)
    explanation_arabic = db.Column(db.Text, nullable=True)

    def __init__(self, title, info, explanation, law_, author):
        self.title = title
        self.info = info
        self.explanation = explanation
        self.posted_at = law_
        self.author = author

    def __repr__(self):
        return 'proposal ' + str(self.id)

    def __meta_data__(self, endpoint):
        data = [
            {
                'name': 'title',
                'content': 'proposal - ' + self.title
            },
            {
                'name': 'description',
                'content': self.info[:155] + '...'
            }
        ]
        return data


class Comment(db.Model):
    __tablename__ = 'comment'
    __bind_key__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    likes = db.Column(db.Integer, nullable=False, default=0)

    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    proposal_id = db.Column(db.Integer, db.ForeignKey('proposal.id'))

    parent_id = db.Column(db.Integer, db.ForeignKey('comment.id'), nullable=False, default=0)
    parent = db.relationship('Comment', remote_side=[id], backref='children')

    def __init__(self, content, proposal, author, parent_comment=None):
        self.content = content
        self.posted_at = proposal
        self.author = author
        self.parent = parent_comment

    def __repr__(self):
        return 'comment ' + str(self.id)


class VotePaper(db.Model):
    __tablename__ = 'vote_paper'
    __bind_key__ = 'law_votes_cast'
    voter_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    law_voted_id = db.Column(db.Integer, db.ForeignKey('law.id'), primary_key=True)
    vote = db.Column(db.Integer)

    law_voted = db.relationship("Law", back_populates="vote_papers")
    user_voted = db.relationship("Users", back_populates="laws_voted_in")

    def __init__(self, vote):
        self.vote = vote


class ConfigurationDB(db.Model):
    __bind_key__ = 'configuration_db'
    id = db.Column(db.Integer, primary_key=True)
    launch_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    week_duel = db.Column(db.Integer, nullable=False, default=1)
    laws_being_discussed = db.Column(db.Integer, nullable=False, default=0)

    def __init__(self):
        pass

    def get_state(self):
        base_date = self.launch_date + timedelta(days=14 * self.week_duel)
        state = {
            'base_date': base_date,
            'week-duel': self.week_duel,
            'laws-being-discussed': self.laws_being_discussed,
            'launch-date': self.launch_date,
            'discussion-start': base_date,
            'discussion-end': base_date + timedelta(days=14),
            'vote-start': base_date - timedelta(days=14),
            'vote-end': base_date,
            'last-voted-start': base_date - timedelta(days=28),
            'last-voted-end': base_date - timedelta(days=14),
            'archive-end':  base_date - timedelta(days=28)
        }

        return state

    def increment_week_duel(self):
        self.week_duel += 1
        self.laws_being_discussed = 0
        db.session.commit()

    def increment_laws_being_discussed(self):
        if self.laws_being_discussed < 6:
            self.laws_being_discussed += 1
            db.session.commmit()
            return True
        else:
            return False


class ServerState:
    @staticmethod
    def get_state():
        return ConfigurationDB.query.get(1).get_state()

    @staticmethod
    def archive_date(week_duel_num: int):
        state = ServerState.get_state()
        start = state['launch-date'] + timedelta(days=14 * week_duel_num)
        end = start + timedelta(days=14)
        return start, end

    @staticmethod
    def increment_laws_being_discussed():
        config = ConfigurationDB.query.get(1)
        if config.laws_being_discussed < 6:
            config.laws_being_discussed += 1
            return True
        else:
            return False

    @staticmethod
    def increment_week_duel():
        config = ConfigurationDB.query.get(1)
        config.week_duel += 1
        config.laws_being_discussed = 0
