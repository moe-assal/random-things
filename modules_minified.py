"""
    TODO: document how to initialize `db` variable.
"""
from white_party import db
from datetime import datetime

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
    """
    Table columns:
        - id: primary key
        - membership id: unique id given for every member
        - description: About me section in user profile
        - password: *****
        - gender: 1 is man. 0 is woman.
        - profile_img: FILENAME of profile image in 'static/profile_img/*********-`original_name`'
            - TODO: check if concatenating original_name of image with random hex string is vulnerable
        - email: g@example.com
        - date joined: Note that this is automated once `Users` instance is created

        - laws_: All the laws posted by the user with backref of `author` in `Law` instances.
        - comments: All the comments posted by the user with backref of `author` in `Comment` instances.
        - proposals: All the proposals posted by the user with backref of `author` in `Proposal` instances.

        - followed: All users the user followed. backref `followers` for `Users` Instances. Many-to-Many relationship
                    using association table `follow_ship_table`

        - proposals_voted_for: ---. backref `voters`. Many-to-Many relationship with Association table
                               `proposals_up_voting_table`
        - comments_liked: ---. backref `users_likes`. Many-to-Many relationship with Association table
                          `comment_likes_table`.
        - laws_voted_in: ---. no backref (Association Object). Many-to-Many relationship using ASSOCIATION OBJECT
                         `VotePaper`.
    """
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


class Law(db.Model):
    """
    Table columns:
        - id: primary key
        - title: ---.
        - info: law's main information that is displayed under title.
        - explanation: ---.
        - date posted: Note that this is automated once `Law` instance is created

        - author_id: one(Users)-to-Many(Laws) relationship with `Users`.
        - edit_proposals: All edit_proposals associated with this law. backref `posted_at`.

        - vote_papers: no backref (Association Object). Many-to-Many relationship using ASSOCIATION OBJECT
                       `VotePaper`.
        - up_votes: ---.
        - down_votes: ---.

        - title_arabic: Translation
        - info_arabic: Translation
        - explanation_arabic: Translation
    """

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


class Proposal(db.Model):
    """
    Table columns:
        - id: primary key
        - title: ---.
        - info: proposal's main information that is displayed under title.
        - explanation: ---.
        - date posted: Note that this is automated once `Proposal` instance is created

        - author_id: one(user)-to-Many(proposals) relationship with `Users`.
        - law_id: one(law)-to-Many(proposals) relationship with `Law`.
        - comments: All comments associated with this law. backref `posted_at`.

        - up_votes: ---.

        - title_arabic: Translation
        - info_arabic: Translation
        - explanation_arabic: Translation
    """
    __tablename__ = 'proposal'
    __bind_key__ = 'proposals'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False, default='title')
    info = db.Column(db.Text, nullable=False)
    explanation = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    law_id = db.Column(db.Integer, db.ForeignKey('law.id'))
    comments = db.relationship('Comment', backref='posted_at')

    up_votes = db.Column(db.Integer, nullable=False, default=0)

    title_arabic = db.Column(db.Text, nullable=True)
    info_arabic = db.Column(db.Text, nullable=True)
    explanation_arabic = db.Column(db.Text, nullable=True)

    def __init__(self, title, info, explanation, law_, author):
        self.title = title
        self.info = info
        self.explanation = explanation
        self.posted_at = law_
        self.author = author


class Comment(db.Model):
    """
        Table columns:
            - id: primary key
            - content: The comment displayed
            - date posted: Note that this is automated once `Comment` instance is created

            - likes: ---.

            - author_id: one(user)-to-Many(comments) relationship with `Users`.
            - proposal_id: one(proposal)-to-Many(comments) relationship with `Proposal`.
            - comments: All comments associated with this law. backref `posted_at`.

            - parent id: One(parent comment)-to-Many(replies). defaults to `0` if comment is a parent and not a reply.
            - parent: Relationship with `Comment`. backref `children`.
        """

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


class VotePaper(db.Model):
    """
        voter_id: `Users` instance id (primary key)
        law_voted_id: `Law` instance id (primary key)
        vote: TODO: document
        law_voted: the relationship with `Law` table above. Backref `vote_papers`
        user_voted: the relationship with `Users` table above. Backref `laws_voted_in`
    """
    __tablename__ = 'vote_paper'
    __bind_key__ = 'law_votes_cast'
    voter_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    law_voted_id = db.Column(db.Integer, db.ForeignKey('law.id'), primary_key=True)
    vote = db.Column(db.Integer)

    law_voted = db.relationship("Law", back_populates="vote_papers")
    user_voted = db.relationship("Users", back_populates="laws_voted_in")

    def __init__(self, vote):
        self.vote = vote

"""
Deletion behavior of each class:
    * Users:
        - When a Users instance gets deleted, there respective Laws and Proposals don't get deleted. They get associated to 
          a Users instance of user_name="unknown" and id=1. There vote cast in VotePaper or proposals_up_voting_table gets 
          deleted. All there respective data from follow_ship_table also gets deleted.
    * Law:
        - When a Law instance gets deleted, the author doesn't get deleted. All the Proposals associated to it gets deleted.
          All the vote casts in VotePaper associated to them gets deleted.
    * Proposal:
        - When a Proposal instance gets deleted, the author doesn't get deleted nor posted_at. 
          All votes in proposals_up_voting_table associated to it gets deleted.
    * VotePaper:
        - When a VotePaper instance gets deleted, only it gets deleted
    * Comment:
        - Only It gets deleted if it is a 'reply' (commment.parent_id != 0). It and it's children (replies) get deleted 
        if it's a parent (commment.parent_id == 0).
"""